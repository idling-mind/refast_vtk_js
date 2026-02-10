/**
 * VTK.js React Component Wrappers for Refast
 *
 * These wrappers adapt react-vtk-js components to work with Refast's
 * component rendering system. They handle prop conversion (snake_case to camelCase)
 * and callback invocation.
 */

import React, { forwardRef, useCallback, useEffect, useRef } from 'react';

// Import VTK.js rendering profiles
import '@kitware/vtk.js/Rendering/Misc/RenderingAPIs';
import '@kitware/vtk.js/Rendering/OpenGL/Profiles/Geometry';
import '@kitware/vtk.js/Rendering/OpenGL/Profiles/Glyph';
import '@kitware/vtk.js/Rendering/OpenGL/Profiles/Volume';

// Import VTK.js sources/filters (needed for Algorithm component to find them by string name)
// These imports register the classes with vtk.js factory, enabling vtkClass="vtkConeSource" etc.
import '@kitware/vtk.js/Filters/Sources/ConeSource';
import '@kitware/vtk.js/Filters/Sources/SphereSource';
import '@kitware/vtk.js/Filters/Sources/CubeSource';
import '@kitware/vtk.js/Filters/Sources/CylinderSource';
import '@kitware/vtk.js/Filters/Sources/PlaneSource';
import '@kitware/vtk.js/Filters/Sources/LineSource';
import '@kitware/vtk.js/Filters/Sources/PointSource';
import '@kitware/vtk.js/Filters/Sources/CircleSource';
import '@kitware/vtk.js/Filters/Sources/ArrowSource';

// Import color transfer function presets (required for colorMapPreset to work)
// The ColorMaps module contains the preset registry that VolumeRepresentation uses
import vtkColorMaps from '@kitware/vtk.js/Rendering/Core/ColorTransferFunction/ColorMaps';

// Force initialization of color map presets by accessing the registry
// This ensures presets are registered before any component tries to use them
const presetNames = vtkColorMaps.rgbPresetNames;
console.log(`[VTK] Color map presets loaded: ${presetNames.length} presets available`);

// Also expose to window for debugging
if (typeof window !== 'undefined') {
  (window as unknown as Record<string, unknown>).__vtkColorMaps = vtkColorMaps;
  (window as unknown as Record<string, unknown>).__vtkColorMapPresetNames = presetNames;
}

// Default fallback preset that is guaranteed to exist in both vtk.js and react-vtk-js color maps
const DEFAULT_COLOR_PRESET = 'erdc_rainbow_bright';

/**
 * Validates a color map preset name and returns a valid preset name.
 * Falls back to DEFAULT_COLOR_PRESET if the requested preset doesn't exist.
 * This prevents "Cannot read properties of undefined (reading 'ColorSpace')" errors.
 */
function getValidColorMapPreset(presetName: string | undefined): string {
  if (!presetName) {
    return DEFAULT_COLOR_PRESET;
  }
  
  // Check if preset exists in the vtk.js ColorMaps registry
  const preset = vtkColorMaps.getPresetByName(presetName);
  if (!preset) {
    console.warn(
      `[VTK] Color map preset "${presetName}" not found. ` +
      `Falling back to "${DEFAULT_COLOR_PRESET}". ` +
      `Available presets: ${presetNames.slice(0, 5).join(', ')}...`
    );
    return DEFAULT_COLOR_PRESET;
  }
  
  return presetName;
}

// Import react-vtk-js components
import {
  View,
  MultiViewRoot,
  GeometryRepresentation,
  Geometry2DRepresentation,
  VolumeRepresentation,
  SliceRepresentation,
  PolyData,
  ImageData,
  Dataset,
  DataArray,
  PointData,
  CellData,
  FieldData,
  Algorithm,
  Reader,
  Picking,
  VolumeController,
  ShareDataSetRoot,
  RegisterDataSet,
  UseDataSet,
} from 'react-vtk-js';

import type {
  PickResult,
} from 'react-vtk-js';

import type { vtkObject } from '@kitware/vtk.js/interfaces';

// Type definitions for VTK data structures (manually defined since not all are exported)
type Matrix3x3 = [number, number, number, number, number, number, number, number, number];
type vtkRange = { min: number; max: number };
type TypedArrayType = 'Uint32Array' | 'Uint16Array' | 'Uint8Array' | 'Int32Array' | 'Int16Array' | 'Int8Array' | 'Float64Array' | 'Float32Array';

// NumpyEncodedArray for binary data from Python
type NumpyDtype = 'int32' | 'int16' | 'int8' | 'uint32' | 'uint16' | 'uint8' | 'float32' | 'float64';
interface NumpyEncodedArray {
  bvals: string;
  dtype: NumpyDtype;
  shape: number[];
}

// DataArrayValues can be a plain array or numpy-encoded binary
type DataArrayValues = number[] | NumpyEncodedArray | Uint8Array | Uint8ClampedArray | Uint16Array | Uint32Array | Int8Array | Int16Array | Int32Array | Float32Array | Float64Array;

// ManipulatorSettings for interactor configuration
interface ManipulatorSettings {
  action: 'Rotate' | 'Pan' | 'Zoom' | 'Roll' | 'ZoomToMouse' | 'Spin';
  button?: number;
  scrollEnabled?: boolean;
  dragEnabled?: boolean;
  useWorldUpVec?: boolean;
  worldUpVec?: [number, number, number];
  useFocalPointAsCenterOfRotation?: boolean;
}

// ============================================================================
// Type Definitions
// ============================================================================

interface CallbackRef {
  callbackId: string;
  boundArgs?: Record<string, unknown>;
}

type CallbackProp = ((data: Record<string, unknown>) => void) | CallbackRef | undefined;


// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Helper to invoke callbacks that may be raw callback refs
 * (for library-managed events) or processed functions (from ComponentRenderer)
 */
function invokeCallback(
  callback: CallbackProp,
  data: Record<string, unknown> = {}
): void {
  if (!callback) return;

  // If it's already a function (processed by ComponentRenderer), call it directly
  if (typeof callback === 'function') {
    callback(data);
    return;
  }

  // If it's a raw callback ref, dispatch the custom event
  if (callback && typeof callback === 'object' && 'callbackId' in callback) {
    const event = new CustomEvent('refast:callback', {
      detail: {
        callbackId: callback.callbackId,
        data: { ...(callback.boundArgs || {}), ...data },
      },
    });
    window.dispatchEvent(event);
  }
}


// ============================================================================
// Camera Sync Manager
// ============================================================================

/**
 * Global manager for synchronizing camera state between views that share
 * the same syncGroup.  When a user rotates/pans/zooms one view, all other
 * views in the same sync group mirror the camera change.
 */

interface CameraSyncEntry {
  viewId: string;
  getCamera: () => any;
  requestRender: () => void;
}

const cameraSyncGroups = new Map<string, Set<CameraSyncEntry>>();
let isCameraSyncing = false;

/**
 * Register a view in a camera sync group.
 * If the group already has members, the new view's camera is immediately
 * synchronised to match the existing views.
 * Returns an unregister function.
 */
function registerCameraSync(group: string, entry: CameraSyncEntry): () => void {
  if (!cameraSyncGroups.has(group)) {
    cameraSyncGroups.set(group, new Set());
  }

  const groupSet = cameraSyncGroups.get(group)!;

  // Sync the newcomer's camera to match existing members
  if (groupSet.size > 0) {
    const existingEntry = groupSet.values().next().value;
    if (existingEntry) {
      const srcCam = existingEntry.getCamera();
      const dstCam = entry.getCamera();
      if (srcCam && dstCam) {
        isCameraSyncing = true;
        dstCam.setPosition(...srcCam.getPosition());
        dstCam.setFocalPoint(...srcCam.getFocalPoint());
        dstCam.setViewUp(...srcCam.getViewUp());
        dstCam.setClippingRange(...srcCam.getClippingRange());
        dstCam.setParallelScale(srcCam.getParallelScale());
        dstCam.setViewAngle(srcCam.getViewAngle());
        entry.requestRender();
        isCameraSyncing = false;
      }
    }
  }

  groupSet.add(entry);

  return () => {
    groupSet.delete(entry);
    if (groupSet.size === 0) {
      cameraSyncGroups.delete(group);
    }
  };
}

/**
 * Copy the sourceCamera's state to every other view in the same sync group.
 */
function broadcastCameraState(
  group: string,
  sourceId: string,
  sourceCamera: any,
): void {
  if (isCameraSyncing) return;
  isCameraSyncing = true;

  try {
    const entries = cameraSyncGroups.get(group);
    if (!entries) return;

    const position = sourceCamera.getPosition();
    const focalPoint = sourceCamera.getFocalPoint();
    const viewUp = sourceCamera.getViewUp();
    const clippingRange = sourceCamera.getClippingRange();
    const parallelScale = sourceCamera.getParallelScale();
    const viewAngle = sourceCamera.getViewAngle();

    for (const entry of entries) {
      if (entry.viewId === sourceId) continue;
      const cam = entry.getCamera();
      if (!cam) continue;

      cam.setPosition(...position);
      cam.setFocalPoint(...focalPoint);
      cam.setViewUp(...viewUp);
      cam.setClippingRange(...clippingRange);
      cam.setParallelScale(parallelScale);
      cam.setViewAngle(viewAngle);
      entry.requestRender();
    }
  } finally {
    isCameraSyncing = false;
  }
}


// ============================================================================
// View Components
// ============================================================================

interface VtkViewProps {
  background?: [number, number, number] | [number, number, number, number];
  interactive?: boolean;
  camera?: Record<string, unknown>;
  autoResetCamera?: boolean;
  interactorSettings?: ManipulatorSettings[];
  autoCenterOfRotation?: boolean;
  syncGroup?: string;
  style?: React.CSSProperties;
  renderWindowStyle?: React.CSSProperties;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkView = forwardRef<unknown, VtkViewProps>((props, ref) => {
  const {
    background,
    interactive,
    camera,
    autoResetCamera,
    interactorSettings,
    autoCenterOfRotation,
    syncGroup,
    style,
    renderWindowStyle,
    className,
    children,
    'data-refast-id': dataRefastId,
  } = props;

  // Ref for the outer wrapper div (used by ResizeObserver)
  const containerRef = useRef<HTMLDivElement>(null);

  // Internal ref to access the react-vtk-js View API (getCamera, requestRender, etc.)
  const internalViewRef = useRef<any>(null);

  // Merge the external forwarded ref with our internal ref
  const mergeRefs = useCallback(
    (instance: any) => {
      internalViewRef.current = instance;
      if (typeof ref === 'function') {
        ref(instance);
      } else if (ref) {
        (ref as React.MutableRefObject<any>).current = instance;
      }
    },
    [ref],
  );

  // Ensure the VTK canvas fills its container and stays crisp on resize.
  //
  // Two things are needed:
  //
  // 1. **Canvas CSS `height: 100%`** — vtk.js creates the <canvas> with only
  //    `style.width = '100%'`; without an explicit CSS height the canvas
  //    relies on its intrinsic aspect-ratio, which leaves whitespace when
  //    the container's aspect-ratio differs from the buffer's.
  //
  // 2. **Pixel-buffer update + synchronous render on resize** — when the
  //    container changes size the canvas buffer (width/height attributes)
  //    must be updated to match.  Crucially, we call `renderWindow.render()`
  //    **synchronously** right after `setSize()`, mirroring what vtk.js's
  //    own `FullScreenRenderWindow.resize()` does.  This ensures the canvas
  //    is cleared *and* re-painted within the same frame — the browser
  //    never paints the blank/cleared buffer, so there is no flicker.
  //
  //    react-vtk-js's built-in ResizeObserver uses deferred rendering
  //    (`queueRender`), which leaves a 1-frame gap between the buffer
  //    clear and the repaint.  Our observer fires in the same delivery
  //    batch; because `setSize` is guarded (same dimensions → no-op),
  //    the library's subsequent call does nothing.
  useEffect(() => {
    const wrapper = containerRef.current;
    if (!wrapper) return;

    let mutationObs: MutationObserver | null = null;

    // --- Canvas CSS patch ------------------------------------------------
    function patchCanvas() {
      const canvas = wrapper.querySelector('canvas');
      if (canvas && !canvas.style.height) {
        canvas.style.height = '100%';
      }
      return !!canvas;
    }

    if (!patchCanvas()) {
      mutationObs = new MutationObserver(() => {
        if (patchCanvas()) {
          mutationObs?.disconnect();
          mutationObs = null;
        }
      });
      mutationObs.observe(wrapper, { childList: true, subtree: true });
    }

    // --- Pixel-buffer resize observer ------------------------------------
    function updateBufferSize() {
      const view = internalViewRef.current;
      if (!view) return;

      const oglrwCtx = view.getOpenGLRenderWindow?.();
      if (!oglrwCtx) return;

      const vtkGLRW = oglrwCtx.get?.();
      const rwContainer = oglrwCtx.getContainer?.();
      if (!vtkGLRW || !rwContainer) return;

      const dpr = window.devicePixelRatio || 1;
      const { width, height } = rwContainer.getBoundingClientRect();
      const w = Math.max(Math.floor(width * dpr), 10);
      const h = Math.max(Math.floor(height * dpr), 10);

      // setSize is a no-op when dimensions haven't changed (vtk.js guard),
      // so a duplicate call from the library's own observer won't flicker.
      const modified = vtkGLRW.setSize(w, h);

      if (modified) {
        // Synchronous render — fills the cleared buffer in the same frame
        // so the browser never paints a blank canvas.  This is the same
        // pattern vtk.js uses in FullScreenRenderWindow.resize().
        const rwCtx = view.getRenderWindow?.();
        const rawRW = rwCtx?.get?.();
        if (rawRW?.render) {
          rawRW.render();
        } else {
          // Fallback: deferred render (may flash, but better than nothing)
          view.requestRender?.();
        }
      }
    }

    const resizeObs = new ResizeObserver(updateBufferSize);
    resizeObs.observe(wrapper);

    return () => {
      mutationObs?.disconnect();
      resizeObs.disconnect();
    };
  }, []);

  // Camera sync effect
  useEffect(() => {
    if (!syncGroup) return;

    let cancelled = false;
    let cleanupFn: (() => void) | null = null;

    // Retry until the VTK camera is available (renderer may still be mounting)
    function setup() {
      if (cancelled) return;
      const view = internalViewRef.current;
      if (!view || !view.getCamera) {
        setTimeout(setup, 50);
        return;
      }
      const camera = view.getCamera();
      if (!camera) {
        setTimeout(setup, 50);
        return;
      }

      const viewId =
        dataRefastId || `vtk-sync-${Math.random().toString(36).slice(2)}`;

      const entry: CameraSyncEntry = {
        viewId,
        getCamera: () => internalViewRef.current?.getCamera?.(),
        // Use getRenderWindow().requestRender() to bypass the Renderer's
        // requestRender path which triggers autoResetCamera. That would
        // undo panned/zoomed camera state by resetting to fit the scene.
        requestRender: () =>
          internalViewRef.current?.getRenderWindow?.()?.requestRender?.(),
      };

      const unregister = registerCameraSync(syncGroup, entry);

      const subscription = camera.onModified(() => {
        if (!isCameraSyncing) {
          broadcastCameraState(syncGroup, viewId, camera);
        }
      });

      cleanupFn = () => {
        unregister();
        subscription.unsubscribe();
      };
    }

    setup();

    return () => {
      cancelled = true;
      cleanupFn?.();
    };
  }, [syncGroup, dataRefastId]);

  return (
    <div
      ref={containerRef}
      id={dataRefastId}
      className={className}
      style={{ position: 'relative', width: '100%', height: '100%', ...style }}
    >
      <View
        ref={mergeRefs}
        background={background}
        interactive={interactive}
        camera={camera}
        autoResetCamera={autoResetCamera}
        interactorSettings={interactorSettings as Parameters<typeof View>[0]['interactorSettings']}
        autoCenterOfRotation={autoCenterOfRotation}
        style={{ width: '100%', height: '100%' }}
        renderWindowStyle={renderWindowStyle}
      >
        {children}
      </View>
    </div>
  );
});

VtkView.displayName = 'VtkView';


interface VtkMultiViewRootProps {
  style?: React.CSSProperties;
  renderWindowStyle?: React.CSSProperties;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkMultiViewRoot = forwardRef<unknown, VtkMultiViewRootProps>((props, _ref) => {
  const {
    style,
    renderWindowStyle,
    className,
    children,
    'data-refast-id': dataRefastId,
  } = props;

  return (
    <div id={dataRefastId} className={className}>
      <MultiViewRoot
        style={style}
        renderWindowStyle={renderWindowStyle}
      >
        {children}
      </MultiViewRoot>
    </div>
  );
});

VtkMultiViewRoot.displayName = 'VtkMultiViewRoot';


// ============================================================================
// Representation Components
// ============================================================================

interface VtkGeometryRepresentationProps {
  id?: string;
  actor?: Record<string, unknown>;
  mapper?: Record<string, unknown>;
  property?: Record<string, unknown>;
  colorMapPreset?: string;
  colorDataRange?: [number, number];
  showCubeAxes?: boolean;
  cubeAxesStyle?: Record<string, unknown>;
  showScalarBar?: boolean;
  scalarBarTitle?: boolean;
  scalarBarStyle?: Record<string, unknown>;
  onDataAvailable?: CallbackProp;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkGeometryRepresentation = forwardRef<unknown, VtkGeometryRepresentationProps>(
  (props, ref) => {
    const {
      id,
      actor,
      mapper,
      property,
      colorMapPreset,
      colorDataRange,
      showCubeAxes,
      cubeAxesStyle,
      showScalarBar,
      scalarBarTitle,
      scalarBarStyle,
      onDataAvailable,
      children,
      'data-refast-id': dataRefastId,
    } = props;

    const handleDataAvailable = useCallback(() => {
      invokeCallback(onDataAvailable, {});
    }, [onDataAvailable]);

    // Validate color map preset to prevent "Cannot read properties of undefined" error
    const validColorMapPreset = colorMapPreset ? getValidColorMapPreset(colorMapPreset) : undefined;

    return (
      <GeometryRepresentation
        ref={ref}
        id={id || dataRefastId}
        actor={actor}
        mapper={mapper}
        property={property}
        colorMapPreset={validColorMapPreset}
        colorDataRange={colorDataRange}
        showCubeAxes={showCubeAxes}
        cubeAxesStyle={cubeAxesStyle}
        showScalarBar={showScalarBar}
        scalarBarTitle={scalarBarTitle}
        scalarBarStyle={scalarBarStyle}
        onDataAvailable={onDataAvailable ? handleDataAvailable : undefined}
      >
        {children}
      </GeometryRepresentation>
    );
  }
);

VtkGeometryRepresentation.displayName = 'VtkGeometryRepresentation';


interface VtkGeometry2DRepresentationProps {
  id?: string;
  actor?: Record<string, unknown>;
  mapper?: Record<string, unknown>;
  property?: Record<string, unknown>;
  colorMapPreset?: string;
  colorDataRange?: [number, number];
  transformCoordinate?: Record<string, unknown>;
  onDataAvailable?: CallbackProp;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkGeometry2DRepresentation = forwardRef<unknown, VtkGeometry2DRepresentationProps>(
  (props, ref) => {
    const {
      id,
      actor,
      mapper,
      property,
      colorMapPreset,
      colorDataRange,
      transformCoordinate,
      onDataAvailable,
      children,
      'data-refast-id': dataRefastId,
    } = props;

    const handleDataAvailable = useCallback(() => {
      invokeCallback(onDataAvailable, {});
    }, [onDataAvailable]);

    // Validate color map preset to prevent "Cannot read properties of undefined" error
    const validColorMapPreset = colorMapPreset ? getValidColorMapPreset(colorMapPreset) : undefined;

    return (
      <Geometry2DRepresentation
        ref={ref}
        id={id || dataRefastId}
        actor={actor}
        mapper={mapper}
        property={property}
        colorMapPreset={validColorMapPreset}
        colorDataRange={colorDataRange}
        transformCoordinate={transformCoordinate}
        onDataAvailable={onDataAvailable ? handleDataAvailable : undefined}
      >
        {children}
      </Geometry2DRepresentation>
    );
  }
);

VtkGeometry2DRepresentation.displayName = 'VtkGeometry2DRepresentation';


interface VtkVolumeRepresentationProps {
  id?: string;
  actor?: Record<string, unknown>;
  mapper?: Record<string, unknown>;
  property?: Record<string, unknown>;
  colorMapPreset?: string;
  colorDataRange?: 'auto' | [number, number];
  onDataAvailable?: CallbackProp;
  onDataChanged?: CallbackProp;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkVolumeRepresentation = forwardRef<unknown, VtkVolumeRepresentationProps>(
  (props, ref) => {
    const {
      id,
      actor,
      mapper,
      property,
      colorMapPreset,
      colorDataRange,
      onDataAvailable,
      onDataChanged,
      children,
      'data-refast-id': dataRefastId,
    } = props;

    const handleDataAvailable = useCallback(() => {
      invokeCallback(onDataAvailable, {});
    }, [onDataAvailable]);

    const handleDataChanged = useCallback(() => {
      invokeCallback(onDataChanged, {});
    }, [onDataChanged]);

    // Validate color map preset to prevent "Cannot read properties of undefined" error
    const validColorMapPreset = colorMapPreset ? getValidColorMapPreset(colorMapPreset) : undefined;

    return (
      <VolumeRepresentation
        ref={ref}
        id={id || dataRefastId}
        actor={actor}
        mapper={mapper}
        property={property}
        colorMapPreset={validColorMapPreset}
        colorDataRange={colorDataRange}
        onDataAvailable={onDataAvailable ? handleDataAvailable : undefined}
        onDataChanged={onDataChanged ? handleDataChanged : undefined}
      >
        {children}
      </VolumeRepresentation>
    );
  }
);

VtkVolumeRepresentation.displayName = 'VtkVolumeRepresentation';


interface VtkSliceRepresentationProps {
  id?: string;
  actor?: Record<string, unknown>;
  mapper?: Record<string, unknown>;
  property?: Record<string, unknown>;
  colorMapPreset?: string;
  colorDataRange?: 'auto' | [number, number];
  iSlice?: number;
  jSlice?: number;
  kSlice?: number;
  xSlice?: number;
  ySlice?: number;
  zSlice?: number;
  onDataAvailable?: CallbackProp;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkSliceRepresentation = forwardRef<unknown, VtkSliceRepresentationProps>(
  (props, ref) => {
    const {
      id,
      actor,
      mapper,
      property,
      colorMapPreset,
      colorDataRange,
      iSlice,
      jSlice,
      kSlice,
      xSlice,
      ySlice,
      zSlice,
      onDataAvailable,
      children,
      'data-refast-id': dataRefastId,
    } = props;

    const handleDataAvailable = useCallback(() => {
      invokeCallback(onDataAvailable, {});
    }, [onDataAvailable]);

    // Validate color map preset to prevent "Cannot read properties of undefined" error
    const validColorMapPreset = colorMapPreset ? getValidColorMapPreset(colorMapPreset) : undefined;

    return (
      <SliceRepresentation
        ref={ref}
        id={id || dataRefastId}
        actor={actor}
        mapper={mapper}
        property={property}
        colorMapPreset={validColorMapPreset}
        colorDataRange={colorDataRange}
        iSlice={iSlice}
        jSlice={jSlice}
        kSlice={kSlice}
        xSlice={xSlice}
        ySlice={ySlice}
        zSlice={zSlice}
        onDataAvailable={onDataAvailable ? handleDataAvailable : undefined}
      >
        {children}
      </SliceRepresentation>
    );
  }
);

VtkSliceRepresentation.displayName = 'VtkSliceRepresentation';


// ============================================================================
// Dataset Components
// ============================================================================

// PolyData cell array type (unsigned integers only)
type CellArrayValues = number[] | NumpyEncodedArray | Uint8Array | Uint8ClampedArray | Uint16Array | Uint32Array;

interface VtkPolyDataProps {
  points?: DataArrayValues;
  verts?: CellArrayValues;
  lines?: CellArrayValues;
  polys?: CellArrayValues;
  strips?: CellArrayValues;
  connectivity?: 'manual' | 'points' | 'triangles' | 'strips';
  port?: number;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkPolyData = forwardRef<unknown, VtkPolyDataProps>((props, ref) => {
  const {
    points,
    verts,
    lines,
    polys,
    strips,
    connectivity,
    port,
    children,
  } = props;

  return (
    <PolyData
      ref={ref}
      points={points}
      verts={verts}
      lines={lines}
      polys={polys}
      strips={strips}
      connectivity={connectivity}
      port={port}
    >
      {children}
    </PolyData>
  );
});

VtkPolyData.displayName = 'VtkPolyData';


interface VtkImageDataProps {
  dimensions?: [number, number, number];
  spacing?: [number, number, number];
  origin?: [number, number, number];
  direction?: Matrix3x3;
  port?: number;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkImageData = forwardRef<unknown, VtkImageDataProps>((props, ref) => {
  const {
    dimensions,
    spacing,
    origin,
    direction,
    port,
    children,
  } = props;

  return (
    <ImageData
      ref={ref}
      dimensions={dimensions}
      spacing={spacing}
      origin={origin}
      direction={direction}
      port={port}
    >
      {children}
    </ImageData>
  );
});

VtkImageData.displayName = 'VtkImageData';


interface VtkDatasetProps {
  dataset?: vtkObject | null;
  className?: string;
  'data-refast-id'?: string;
}

export const VtkDataset: React.FC<VtkDatasetProps> = (props) => {
  const { dataset } = props;

  return <Dataset dataset={dataset ?? null} />;
};

VtkDataset.displayName = 'VtkDataset';


// ============================================================================
// Data Array Components
// ============================================================================

interface VtkDataArrayProps {
  name?: string;
  type?: TypedArrayType;
  values?: DataArrayValues;
  numberOfComponents?: number;
  registration?: string;
  range?: vtkRange;
  className?: string;
  'data-refast-id'?: string;
}

export const VtkDataArray: React.FC<VtkDataArrayProps> = (props) => {
  const {
    name,
    type,
    values,
    numberOfComponents,
    registration,
    range,
  } = props;

  return (
    <DataArray
      name={name}
      type={type}
      values={values}
      numberOfComponents={numberOfComponents}
      registration={registration}
      range={range}
    />
  );
};

VtkDataArray.displayName = 'VtkDataArray';


interface VtkPointDataProps {
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkPointData: React.FC<VtkPointDataProps> = (props) => {
  const { children } = props;
  return <PointData>{children}</PointData>;
};

VtkPointData.displayName = 'VtkPointData';


interface VtkCellDataProps {
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkCellData: React.FC<VtkCellDataProps> = (props) => {
  const { children } = props;
  return <CellData>{children}</CellData>;
};

VtkCellData.displayName = 'VtkCellData';


interface VtkFieldDataProps {
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkFieldData: React.FC<VtkFieldDataProps> = (props) => {
  const { children } = props;
  return <FieldData>{children}</FieldData>;
};

VtkFieldData.displayName = 'VtkFieldData';


// ============================================================================
// Algorithm & Reader Components
// ============================================================================

interface VtkAlgorithmProps {
  vtkClass: string;
  state?: Record<string, unknown>;
  port?: number;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkAlgorithm: React.FC<VtkAlgorithmProps> = (props) => {
  const { vtkClass, state, port, children } = props;

  return (
    <Algorithm vtkClass={vtkClass} state={state} port={port}>
      {children}
    </Algorithm>
  );
};

VtkAlgorithm.displayName = 'VtkAlgorithm';


interface VtkReaderProps {
  vtkClass: string;
  url?: string;
  urlOptions?: Record<string, unknown>;
  arrayBuffer?: ArrayBuffer;
  base64ArrayBuffer?: string;
  text?: string;
  port?: number;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkReader: React.FC<VtkReaderProps> = (props) => {
  const {
    vtkClass,
    url,
    urlOptions,
    arrayBuffer,
    base64ArrayBuffer,
    text,
    port,
    children,
  } = props;

  return (
    <Reader
      vtkClass={vtkClass}
      url={url}
      urlOptions={urlOptions}
      arrayBuffer={arrayBuffer}
      base64ArrayBuffer={base64ArrayBuffer}
      text={text}
      port={port}
    >
      {children}
    </Reader>
  );
};

VtkReader.displayName = 'VtkReader';


// ============================================================================
// Interaction Components
// ============================================================================

interface VtkPickingProps {
  enabled?: boolean;
  onHover?: CallbackProp;
  onClick?: CallbackProp;
  onPointerDown?: CallbackProp;
  onPointerUp?: CallbackProp;
  pointerSize?: number;
  onHoverDebounceWait?: number;
  className?: string;
  'data-refast-id'?: string;
}

export const VtkPicking = forwardRef<unknown, VtkPickingProps>((props, ref) => {
  const {
    enabled,
    onHover,
    onClick,
    onPointerDown,
    onPointerUp,
    pointerSize,
    onHoverDebounceWait,
  } = props;

  const handleHover = useCallback(
    (selection: PickResult, event: React.PointerEvent) => {
      invokeCallback(onHover, {
        selection: selection as unknown as Record<string, unknown>,
        clientX: event.clientX,
        clientY: event.clientY,
      });
    },
    [onHover]
  );

  const handleClick = useCallback(
    (selection: PickResult, event: React.MouseEvent) => {
      invokeCallback(onClick, {
        selection: selection as unknown as Record<string, unknown>,
        clientX: event.clientX,
        clientY: event.clientY,
      });
    },
    [onClick]
  );

  const handlePointerDown = useCallback(
    (selection: PickResult, event: React.PointerEvent) => {
      invokeCallback(onPointerDown, {
        selection: selection as unknown as Record<string, unknown>,
        clientX: event.clientX,
        clientY: event.clientY,
      });
    },
    [onPointerDown]
  );

  const handlePointerUp = useCallback(
    (selection: PickResult, event: React.PointerEvent) => {
      invokeCallback(onPointerUp, {
        selection: selection as unknown as Record<string, unknown>,
        clientX: event.clientX,
        clientY: event.clientY,
      });
    },
    [onPointerUp]
  );

  return (
    <Picking
      ref={ref}
      enabled={enabled}
      onHover={onHover ? handleHover : undefined}
      onClick={onClick ? handleClick : undefined}
      onPointerDown={onPointerDown ? handlePointerDown : undefined}
      onPointerUp={onPointerUp ? handlePointerUp : undefined}
      pointerSize={pointerSize}
      onHoverDebounceWait={onHoverDebounceWait}
    />
  );
});

VtkPicking.displayName = 'VtkPicking';


interface VtkVolumeControllerProps {
  size?: [number, number];
  rescaleColorMap?: boolean;
  className?: string;
  'data-refast-id'?: string;
}

export const VtkVolumeController: React.FC<VtkVolumeControllerProps> = (props) => {
  const { size, rescaleColorMap } = props;

  return <VolumeController size={size} rescaleColorMap={rescaleColorMap} />;
};

VtkVolumeController.displayName = 'VtkVolumeController';


// ============================================================================
// Data Sharing Components
// ============================================================================

interface VtkShareDataSetRootProps {
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkShareDataSetRoot: React.FC<VtkShareDataSetRootProps> = (props) => {
  const { children } = props;
  return <ShareDataSetRoot>{children}</ShareDataSetRoot>;
};

VtkShareDataSetRoot.displayName = 'VtkShareDataSetRoot';


interface VtkRegisterDataSetProps {
  datasetId: string;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

export const VtkRegisterDataSet: React.FC<VtkRegisterDataSetProps> = (props) => {
  const { datasetId, children } = props;
  return <RegisterDataSet id={datasetId}>{children}</RegisterDataSet>;
};

VtkRegisterDataSet.displayName = 'VtkRegisterDataSet';


interface VtkUseDataSetProps {
  datasetId: string;
  port?: number;
  className?: string;
  'data-refast-id'?: string;
}

export const VtkUseDataSet: React.FC<VtkUseDataSetProps> = (props) => {
  const { datasetId, port } = props;
  return <UseDataSet id={datasetId} port={port} />;
};

VtkUseDataSet.displayName = 'VtkUseDataSet';
