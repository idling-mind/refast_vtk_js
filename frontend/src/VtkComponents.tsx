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
import vtkAxesActor from '@kitware/vtk.js/Rendering/Core/AxesActor';
import vtkCubeAxesActor from '@kitware/vtk.js/Rendering/Core/CubeAxesActor';
import vtkScalarBarActor from '@kitware/vtk.js/Rendering/Core/ScalarBarActor';
import vtkOrientationMarkerWidget from '@kitware/vtk.js/Interaction/Widgets/OrientationMarkerWidget';

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

// react-vtk-js v2 currently declares scalar bar / cube axes props in types,
// but its GeometryRepresentation runtime does not apply them.
// Use internal contexts to attach those actors explicitly.
import {
  useRendererContext,
  useRepresentationContext,
} from 'react-vtk-js/dist/esm/core/contexts';

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
    const wrapperEl = containerRef.current;
    if (!wrapperEl) return;

    let mutationObs: MutationObserver | null = null;

    // --- Canvas CSS patch ------------------------------------------------
    function patchCanvas() {
      const canvas = wrapperEl!.querySelector('canvas');
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
      mutationObs.observe(wrapperEl, { childList: true, subtree: true });
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

      // Apply the new pixel-buffer size.  setSize is a no-op when the
      // dimensions haven't changed, but we always follow up with a
      // synchronous render regardless of the return value.
      //
      // Why not gate on `modified`?
      // When views share a camera-sync group, broadcastCameraState() calls
      // requestRender() on peer views.  That deferred render can internally
      // call setSize(), consuming the pending size change *before* our
      // ResizeObserver callback fires.  setSize then returns false here,
      // the synchronous render is skipped, and the browser paints the
      // cleared (blank) buffer — causing flicker.
      //
      // Always rendering synchronously is cheap because this callback only
      // fires on actual container size changes (ResizeObserver guarantee),
      // and vtk.js's render pipeline skips redundant GPU work internally.
      vtkGLRW.setSize(w, h);

      // Synchronous render — fills the buffer in the same frame so the
      // browser never paints a blank canvas.  Same pattern vtk.js uses
      // in FullScreenRenderWindow.resize().
      const rwCtx = view.getRenderWindow?.();
      const rawRW = rwCtx?.get?.();
      if (rawRW?.render) {
        rawRW.render();
      } else {
        // Fallback: deferred render (may flash, but better than nothing)
        view.requestRender?.();
      }
    }

    const resizeObs = new ResizeObserver(updateBufferSize);
    resizeObs.observe(wrapperEl);

    return () => {
      mutationObs?.disconnect();
      resizeObs.disconnect();
    };
  }, []);

  // Camera sync effect
  useEffect(() => {
    console.log(`[VTK] Setting up camera sync for group "${syncGroup}" (View ID: ${dataRefastId})`);
    if (!syncGroup) return;
    const syncGroupName = syncGroup;

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

      const unregister = registerCameraSync(syncGroupName, entry);

      const subscription = camera.onModified(() => {
        if (!isCameraSyncing) {
          broadcastCameraState(syncGroupName, viewId, camera);
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

  // Expose imperative methods on the wrapper DOM element so Python can call
  // them with ctx.bound_js(...) / ctx.call_bound_js(...).
  useEffect(() => {
    const wrapper = containerRef.current;
    if (!wrapper) return;

    const resetCamera = () => {
      const view = internalViewRef.current;
      if (!view) return;
      view.resetCamera?.();
      view.requestRender?.();
    };

    const requestRender = () => {
      internalViewRef.current?.requestRender?.();
    };

    (wrapper as any).resetCamera = resetCamera;
    (wrapper as any).reset_camera = resetCamera;
    (wrapper as any).requestRender = requestRender;
    (wrapper as any).request_render = requestRender;

    return () => {
      delete (wrapper as any).resetCamera;
      delete (wrapper as any).reset_camera;
      delete (wrapper as any).requestRender;
      delete (wrapper as any).request_render;
    };
  }, []);

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


interface VtkAxesActorProps {
  visible?: boolean;
  size?: number | [number, number, number];
  config?: Record<string, unknown>;
  xConfig?: Record<string, unknown>;
  yConfig?: Record<string, unknown>;
  zConfig?: Record<string, unknown>;
  recenter?: boolean;
  xAxisInvert?: boolean;
  yAxisInvert?: boolean;
  zAxisInvert?: boolean;
  fixedInWindow?: boolean;
  markerCorner?: 'TOP_LEFT' | 'TOP_RIGHT' | 'BOTTOM_LEFT' | 'BOTTOM_RIGHT' | string;
  markerViewportSize?: number;
  markerMinPixelSize?: number;
  markerMaxPixelSize?: number;
  axisLabelsEnabled?: boolean;
  axisLabels?: Record<string, unknown>;
  axisLabelStyle?: Record<string, unknown>;
  className?: string;
  'data-refast-id'?: string;
}

export const VtkAxesActor: React.FC<VtkAxesActorProps> = (props) => {
  const {
    visible = true,
    size,
    config,
    xConfig,
    yConfig,
    zConfig,
    recenter,
    xAxisInvert,
    yAxisInvert,
    zAxisInvert,
    fixedInWindow = false,
    markerCorner = 'BOTTOM_LEFT',
    markerViewportSize = 0.2,
    markerMinPixelSize = 50,
    markerMaxPixelSize = 200,
    axisLabelsEnabled = false,
    axisLabels,
    axisLabelStyle,
  } = props;

  const renderer = useRendererContext();
  const axesActorRef = useRef<any>(null);
  const markerActorRef = useRef<any>(null);
  const markerWidgetRef = useRef<any>(null);
  const labelsOverlayRef = useRef<HTMLDivElement | null>(null);
  const labelSubscriptionsRef = useRef<Array<{ unsubscribe: () => void }>>([]);
  const labelResizeObserverRef = useRef<ResizeObserver | null>(null);

  const cleanupWorldActor = useCallback(() => {
    const vtkRenderer = renderer.get?.();
    if (vtkRenderer && axesActorRef.current) {
      vtkRenderer.removeActor(axesActorRef.current);
    }
    axesActorRef.current?.delete?.();
    axesActorRef.current = null;
  }, [renderer]);

  const cleanupMarkerWidget = useCallback(() => {
    markerWidgetRef.current?.setEnabled?.(false);
    markerWidgetRef.current?.delete?.();
    markerWidgetRef.current = null;
    markerActorRef.current?.delete?.();
    markerActorRef.current = null;
  }, []);

  const cleanupLabelOverlay = useCallback(() => {
    labelResizeObserverRef.current?.disconnect();
    labelResizeObserverRef.current = null;

    for (const sub of labelSubscriptionsRef.current) {
      sub.unsubscribe();
    }
    labelSubscriptionsRef.current = [];

    if (labelsOverlayRef.current?.parentElement) {
      labelsOverlayRef.current.parentElement.removeChild(labelsOverlayRef.current);
    }
    labelsOverlayRef.current = null;
  }, []);

  const applyAxesConfig = useCallback(
    (axesActor: any) => {
      if (typeof axesActor.setVisibility === 'function') {
        axesActor.setVisibility(!!visible);
      }

      if (typeof size === 'number' && typeof axesActor.setScale === 'function') {
        axesActor.setScale(size, size, size);
      } else if (Array.isArray(size) && size.length === 3 && typeof axesActor.setScale === 'function') {
        axesActor.setScale(size[0], size[1], size[2]);
      }

      if (config && typeof axesActor.getConfig === 'function' && typeof axesActor.setConfig === 'function') {
        axesActor.setConfig({ ...axesActor.getConfig(), ...config });
      }

      if (typeof recenter === 'boolean' && typeof axesActor.getConfig === 'function' && typeof axesActor.setConfig === 'function') {
        axesActor.setConfig({ ...axesActor.getConfig(), recenter: recenter });
      }

      if (xConfig && typeof axesActor.getXConfig === 'function' && typeof axesActor.setXConfig === 'function') {
        axesActor.setXConfig({ ...axesActor.getXConfig(), ...xConfig });
      }

      if (yConfig && typeof axesActor.getYConfig === 'function' && typeof axesActor.setYConfig === 'function') {
        axesActor.setYConfig({ ...axesActor.getYConfig(), ...yConfig });
      }

      if (zConfig && typeof axesActor.getZConfig === 'function' && typeof axesActor.setZConfig === 'function') {
        axesActor.setZConfig({ ...axesActor.getZConfig(), ...zConfig });
      }

      if (typeof xAxisInvert === 'boolean' && typeof axesActor.getXConfig === 'function' && typeof axesActor.setXConfig === 'function') {
        axesActor.setXConfig({ ...axesActor.getXConfig(), invert: xAxisInvert });
      }

      if (typeof yAxisInvert === 'boolean' && typeof axesActor.getYConfig === 'function' && typeof axesActor.setYConfig === 'function') {
        axesActor.setYConfig({ ...axesActor.getYConfig(), invert: yAxisInvert });
      }

      if (typeof zAxisInvert === 'boolean' && typeof axesActor.getZConfig === 'function' && typeof axesActor.setZConfig === 'function') {
        axesActor.setZConfig({ ...axesActor.getZConfig(), invert: zAxisInvert });
      }

      if (typeof axesActor.update === 'function') {
        axesActor.update();
      }
    },
    [
      visible,
      size,
      config,
      xConfig,
      yConfig,
      zConfig,
      recenter,
      xAxisInvert,
      yAxisInvert,
      zAxisInvert,
    ]
  );

  useEffect(() => {
    const vtkRenderer = renderer.get?.();
    if (!vtkRenderer) {
      return;
    }

    cleanupWorldActor();
    cleanupMarkerWidget();
    cleanupLabelOverlay();

    const interactor = vtkRenderer.getRenderWindow?.()?.getInteractor?.();

    const attachTextLabels = (
      targetRenderer: any,
      targetActor: any,
      mode: 'fixed' | 'world'
    ) => {
      if (!interactor) {
        return;
      }

      const container = interactor.getContainer?.();
      const view = interactor.getView?.();
      if (!targetRenderer || !container || !view) {
        return;
      }

      const overlay = document.createElement('div');
      overlay.style.position = 'absolute';
      overlay.style.left = '0';
      overlay.style.top = '0';
      overlay.style.width = '100%';
      overlay.style.height = '100%';
      overlay.style.pointerEvents = 'none';
      overlay.style.zIndex = '2';

      const makeLabel = (text: string) => {
        const el = document.createElement('div');
        const css = axisLabelStyle || {};
        const color = String(css.color ?? css.fontColor ?? css.font_color ?? '#ffffff');
        const fontSize = String(css.fontSize ?? css.font_size ?? '13px');
        const fontWeight = String(css.fontWeight ?? css.font_weight ?? 700);

        el.textContent = text;
        el.style.position = 'absolute';
        el.style.color = color;
        el.style.fontSize = fontSize;
        el.style.fontWeight = fontWeight;
        el.style.textShadow = '0 1px 2px rgba(0,0,0,0.65)';
        el.style.transform = 'translate(-50%, -50%)';
        overlay.appendChild(el);
        return el;
      };

      const labels = axisLabels || {};
      const xLabel = makeLabel(String(labels.x ?? labels.x_label ?? labels.xPlus ?? labels.x_plus ?? 'X'));
      const yLabel = makeLabel(String(labels.y ?? labels.y_label ?? labels.yPlus ?? labels.y_plus ?? 'Y'));
      const zLabel = makeLabel(String(labels.z ?? labels.z_label ?? labels.zPlus ?? labels.z_plus ?? 'Z'));

      labelsOverlayRef.current = overlay;
      container.appendChild(overlay);

      const getTipCoordinates = (): Record<'x' | 'y' | 'z', [number, number, number]> => {
        const cfg = (config || {}) as Record<string, unknown>;
        const centered = typeof recenter === 'boolean' ? recenter : (cfg.recenter as boolean | undefined) ?? true;
        const baseTip = centered ? 0.56 : 1.06;

        let sx = 1;
        let sy = 1;
        let sz = 1;
        if (typeof size === 'number') {
          sx = size;
          sy = size;
          sz = size;
        } else if (Array.isArray(size) && size.length === 3) {
          sx = Number(size[0]) || 1;
          sy = Number(size[1]) || 1;
          sz = Number(size[2]) || 1;
        }

        const xInv = typeof xAxisInvert === 'boolean' ? xAxisInvert : (xConfig?.invert as boolean | undefined) ?? false;
        const yInv = typeof yAxisInvert === 'boolean' ? yAxisInvert : (yConfig?.invert as boolean | undefined) ?? false;
        const zInv = typeof zAxisInvert === 'boolean' ? zAxisInvert : (zConfig?.invert as boolean | undefined) ?? false;

        const actorPos = mode === 'world' ? (targetActor.getPosition?.() ?? [0, 0, 0]) : [0, 0, 0];

        return {
          x: [actorPos[0] + (xInv ? -baseTip : baseTip) * sx, actorPos[1], actorPos[2]],
          y: [actorPos[0], actorPos[1] + (yInv ? -baseTip : baseTip) * sy, actorPos[2]],
          z: [actorPos[0], actorPos[1], actorPos[2] + (zInv ? -baseTip : baseTip) * sz],
        };
      };

      const updateOverlayPositions = () => {
        const canvas = view.getCanvas?.();
        if (!canvas) {
          return;
        }

        const canvasHeight = canvas.height;
        const tips = getTipCoordinates();

        const positionLabel = (el: HTMLDivElement, point: [number, number, number], dx: number, dy: number) => {
          const display = view.worldToDisplay(point[0], point[1], point[2], targetRenderer);
          const x = display[0] + dx;
          const y = canvasHeight - display[1] + dy;
          el.style.left = `${x}px`;
          el.style.top = `${y}px`;
        };

        positionLabel(xLabel, tips.x, 10, 0);
        positionLabel(yLabel, tips.y, 0, -10);
        positionLabel(zLabel, tips.z, 8, 8);
      };

      updateOverlayPositions();

      const camera = vtkRenderer.getActiveCamera?.();
      if (camera?.onModified) {
        labelSubscriptionsRef.current.push(camera.onModified(updateOverlayPositions));
      }
      if (interactor.onAnimation) {
        labelSubscriptionsRef.current.push(interactor.onAnimation(updateOverlayPositions));
      }
      if (interactor.onEndAnimation) {
        labelSubscriptionsRef.current.push(interactor.onEndAnimation(updateOverlayPositions));
      }

      labelResizeObserverRef.current = new ResizeObserver(() => {
        updateOverlayPositions();
      });
      labelResizeObserverRef.current.observe(container);
    };

    if (!fixedInWindow) {
      axesActorRef.current = vtkAxesActor.newInstance();
      vtkRenderer.addActor(axesActorRef.current);
      applyAxesConfig(axesActorRef.current);

      if (axisLabelsEnabled) {
        attachTextLabels(vtkRenderer, axesActorRef.current, 'world');
      }

      renderer.requestRender();

      return () => {
        cleanupWorldActor();
        cleanupLabelOverlay();
        renderer.requestRender();
      };
    }
    if (!interactor) {
      return;
    }

    markerActorRef.current = vtkAxesActor.newInstance();
    applyAxesConfig(markerActorRef.current);

    markerWidgetRef.current = vtkOrientationMarkerWidget.newInstance({
      actor: markerActorRef.current,
      interactor: interactor,
      parentRenderer: vtkRenderer,
    });

    const validCorners = new Set(['TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_LEFT', 'BOTTOM_RIGHT']);
    const normalizedCorner = String(markerCorner).toUpperCase();
    const resolvedCorner = validCorners.has(normalizedCorner) ? normalizedCorner : 'BOTTOM_LEFT';

    markerWidgetRef.current.setViewportCorner?.(resolvedCorner);
    markerWidgetRef.current.setViewportSize?.(markerViewportSize);
    markerWidgetRef.current.setMinPixelSize?.(markerMinPixelSize);
    markerWidgetRef.current.setMaxPixelSize?.(markerMaxPixelSize);
    markerWidgetRef.current.setEnabled?.(!!visible);
    markerWidgetRef.current.updateMarkerOrientation?.();

    if (axisLabelsEnabled) {
      const markerRenderer = markerWidgetRef.current.getRenderer?.();
      if (markerRenderer) {
        attachTextLabels(markerRenderer, markerActorRef.current, 'fixed');
      }
    }

    renderer.requestRender();

    return () => {
      cleanupMarkerWidget();
      cleanupLabelOverlay();
      renderer.requestRender();
    };
  }, [
    renderer,
    fixedInWindow,
    markerCorner,
    markerViewportSize,
    markerMinPixelSize,
    markerMaxPixelSize,
    axisLabelsEnabled,
    cleanupWorldActor,
    cleanupMarkerWidget,
    cleanupLabelOverlay,
    applyAxesConfig,
    axisLabels,
    axisLabelStyle,
    size,
    recenter,
    xAxisInvert,
    yAxisInvert,
    zAxisInvert,
    config,
    xConfig,
    yConfig,
    zConfig,
    visible,
  ]);

  return null;
};

VtkAxesActor.displayName = 'VtkAxesActor';


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
  scalarBarTitle?: boolean | string;
  scalarBarStyle?: Record<string, unknown>;
  onDataAvailable?: CallbackProp;
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

interface GeometryDecorationProps {
  showCubeAxes?: boolean;
  cubeAxesStyle?: Record<string, unknown>;
  showScalarBar?: boolean;
  scalarBarTitle?: boolean | string;
  scalarBarStyle?: Record<string, unknown>;
}

function toBounds6(input: unknown): [number, number, number, number, number, number] | null {
  if (!Array.isArray(input) || input.length !== 6) {
    return null;
  }

  const values = input.map((v) => Number(v));
  if (values.some((v) => Number.isNaN(v) || !Number.isFinite(v))) {
    return null;
  }

  return [
    values[0],
    values[1],
    values[2],
    values[3],
    values[4],
    values[5],
  ];
}

function GeometryDecorationActors({
  showCubeAxes,
  cubeAxesStyle,
  showScalarBar,
  scalarBarTitle,
  scalarBarStyle,
}: GeometryDecorationProps): null {
  const renderer = useRendererContext();
  const representation = useRepresentationContext();
  const cubeAxesRef = useRef<any>(null);
  const scalarBarRef = useRef<any>(null);

  const syncActors = useCallback(() => {
    const vtkRenderer = renderer.get?.();
    const vtkMapper = representation.getMapper?.() as any;
    const vtkActor = representation.getActor?.() as any;

    if (!vtkRenderer) {
      return;
    }

    if (showCubeAxes) {
      if (!cubeAxesRef.current) {
        cubeAxesRef.current = vtkCubeAxesActor.newInstance();
        vtkRenderer.addActor(cubeAxesRef.current);
      }

      const cubeAxes = cubeAxesRef.current;
      const bounds = toBounds6(vtkMapper?.getBounds?.() ?? vtkActor?.getBounds?.());
      const camera = vtkRenderer.getActiveCamera?.();

      if (bounds) {
        cubeAxes.setDataBounds(bounds);
      }
      if (camera) {
        cubeAxes.setCamera(camera);
      }
      if (cubeAxesStyle && typeof cubeAxes.set === 'function') {
        cubeAxes.set(cubeAxesStyle);
      }
    } else if (cubeAxesRef.current) {
      vtkRenderer.removeActor(cubeAxesRef.current);
      cubeAxesRef.current.delete?.();
      cubeAxesRef.current = null;
    }

    if (showScalarBar) {
      if (!scalarBarRef.current) {
        scalarBarRef.current = vtkScalarBarActor.newInstance();
        vtkRenderer.addActor(scalarBarRef.current);
      }

      const scalarBar = scalarBarRef.current;
      const lookupTable = vtkMapper?.getLookupTable?.();
      if (lookupTable) {
        scalarBar.setScalarsToColors(lookupTable);
      }

      if (typeof scalarBarTitle === 'string') {
        scalarBar.setAxisLabel(scalarBarTitle);
      } else if (scalarBarTitle === false) {
        scalarBar.setAxisLabel('');
      }

      if (scalarBarStyle && typeof scalarBar.set === 'function') {
        scalarBar.set(scalarBarStyle);
      }
    } else if (scalarBarRef.current) {
      vtkRenderer.removeActor(scalarBarRef.current);
      scalarBarRef.current.delete?.();
      scalarBarRef.current = null;
    }

    renderer.requestRender();
  }, [
    renderer,
    representation,
    showCubeAxes,
    cubeAxesStyle,
    showScalarBar,
    scalarBarTitle,
    scalarBarStyle,
  ]);

  useEffect(() => {
    syncActors();

    const unsubscribeAvailable = representation.onDataAvailable?.(() => {
      syncActors();
    });
    const unsubscribeChanged = representation.onDataChanged?.(() => {
      syncActors();
    });

    return () => {
      unsubscribeAvailable?.();
      unsubscribeChanged?.();

      const vtkRenderer = renderer.get?.();
      if (vtkRenderer && cubeAxesRef.current) {
        vtkRenderer.removeActor(cubeAxesRef.current);
        cubeAxesRef.current.delete?.();
        cubeAxesRef.current = null;
      }
      if (vtkRenderer && scalarBarRef.current) {
        vtkRenderer.removeActor(scalarBarRef.current);
        scalarBarRef.current.delete?.();
        scalarBarRef.current = null;
      }
    };
  }, [renderer, representation, syncActors]);

  return null;
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

    // Scalar bar visibility depends on scalar-aware mapper settings.
    // Apply safe defaults when scalar bar is enabled but mapper options are omitted.
    const resolvedMapper = showScalarBar
      ? {
          scalarVisibility: true,
          interpolateScalarsBeforeMapping: true,
          useLookupTableScalarRange: true,
          ...(mapper || {}),
        }
      : mapper;

    return (
      <GeometryRepresentation
        ref={ref}
        id={id || dataRefastId}
        actor={actor}
        mapper={resolvedMapper}
        property={property}
        colorMapPreset={validColorMapPreset}
        colorDataRange={colorDataRange}
        showCubeAxes={showCubeAxes}
        cubeAxesStyle={cubeAxesStyle}
        showScalarBar={showScalarBar}
        scalarBarTitle={
          typeof scalarBarTitle === 'boolean'
            ? scalarBarTitle
            : scalarBarTitle
              ? true
              : undefined
        }
        scalarBarStyle={scalarBarStyle}
        onDataAvailable={onDataAvailable ? handleDataAvailable : undefined}
      >
        <GeometryDecorationActors
          showCubeAxes={showCubeAxes}
          cubeAxesStyle={cubeAxesStyle}
          showScalarBar={showScalarBar}
          scalarBarTitle={scalarBarTitle}
          scalarBarStyle={scalarBarStyle}
        />
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
