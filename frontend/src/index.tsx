/**
 * Refast VTK.js Extension
 *
 * This extension provides VTK.js 3D visualization components for Refast.
 *
 * The components are registered with RefastClient's component registry
 * when this script loads after refast-client.js.
 */

// Import all VTK component wrappers
import {
  VtkView,
  VtkAxesActor,
  VtkMultiViewRoot,
  VtkGeometryRepresentation,
  VtkGeometry2DRepresentation,
  VtkVolumeRepresentation,
  VtkSliceRepresentation,
  VtkPolyData,
  VtkImageData,
  VtkDataset,
  VtkDataArray,
  VtkPointData,
  VtkCellData,
  VtkFieldData,
  VtkAlgorithm,
  VtkThresholdPoints,
  VtkReader,
  VtkPicking,
  VtkVolumeController,
  VtkShareDataSetRoot,
  VtkRegisterDataSet,
  VtkUseDataSet,
  VtkAnnotation,
  VtkAnnotations,
} from './VtkComponents';

// Type definition for RefastClient
interface RefastClient {
  componentRegistry: {
    register: (name: string, component: React.ComponentType<unknown>) => void;
    has: (name: string) => boolean;
  };
  React: typeof import('react');
  ReactDOM: typeof import('react-dom');
  version: string;
}

declare global {
  interface Window {
    RefastClient?: RefastClient;
  }
}

// Component registration map
const COMPONENTS: Record<string, React.ComponentType<unknown>> = {
  // View components
  VtkView: VtkView as React.ComponentType<unknown>,
  VtkAxesActor: VtkAxesActor as React.ComponentType<unknown>,
  VtkMultiViewRoot: VtkMultiViewRoot as React.ComponentType<unknown>,
  // Representation components
  VtkGeometryRepresentation: VtkGeometryRepresentation as React.ComponentType<unknown>,
  VtkGeometry2DRepresentation: VtkGeometry2DRepresentation as React.ComponentType<unknown>,
  VtkVolumeRepresentation: VtkVolumeRepresentation as React.ComponentType<unknown>,
  VtkSliceRepresentation: VtkSliceRepresentation as React.ComponentType<unknown>,
  // Dataset components
  VtkPolyData: VtkPolyData as React.ComponentType<unknown>,
  VtkImageData: VtkImageData as React.ComponentType<unknown>,
  VtkDataset: VtkDataset as React.ComponentType<unknown>,
  // Data array components
  VtkDataArray: VtkDataArray as React.ComponentType<unknown>,
  VtkPointData: VtkPointData as React.ComponentType<unknown>,
  VtkCellData: VtkCellData as React.ComponentType<unknown>,
  VtkFieldData: VtkFieldData as React.ComponentType<unknown>,
  // Algorithm & Reader
  VtkAlgorithm: VtkAlgorithm as React.ComponentType<unknown>,
  VtkThresholdPoints: VtkThresholdPoints as React.ComponentType<unknown>,
  VtkReader: VtkReader as React.ComponentType<unknown>,
  // Interaction
  VtkPicking: VtkPicking as React.ComponentType<unknown>,
  VtkVolumeController: VtkVolumeController as React.ComponentType<unknown>,
  // Data sharing
  VtkShareDataSetRoot: VtkShareDataSetRoot as React.ComponentType<unknown>,
  VtkRegisterDataSet: VtkRegisterDataSet as React.ComponentType<unknown>,
  VtkUseDataSet: VtkUseDataSet as React.ComponentType<unknown>,
  VtkAnnotation: VtkAnnotation as React.ComponentType<unknown>,
  VtkAnnotations: VtkAnnotations as React.ComponentType<unknown>,
};

/**
 * Register all VTK components with Refast.
 *
 * This function is called immediately when the script loads.
 * It checks for RefastClient and registers all components.
 */
function registerComponents(): void {
  if (!window.RefastClient) {
    console.error(
      '[refast-vtk-js] RefastClient not found. ' +
      'Make sure refast-client.js is loaded before this script.'
    );
    return;
  }

  const { componentRegistry } = window.RefastClient;

  // Register all components
  for (const [name, component] of Object.entries(COMPONENTS)) {
    if (componentRegistry.has(name)) {
      console.warn(`[refast-vtk-js] ${name} already registered, skipping.`);
      continue;
    }

    componentRegistry.register(name, component);
    console.log(`[refast-vtk-js] Registered ${name} component`);
  }

  console.log(`[refast-vtk-js] Registered ${Object.keys(COMPONENTS).length} VTK components`);
}

// Register components immediately
registerComponents();

// Export for direct imports (if bundled differently)
export {
  VtkView,
  VtkAxesActor,
  VtkMultiViewRoot,
  VtkGeometryRepresentation,
  VtkGeometry2DRepresentation,
  VtkVolumeRepresentation,
  VtkSliceRepresentation,
  VtkPolyData,
  VtkImageData,
  VtkDataset,
  VtkDataArray,
  VtkPointData,
  VtkCellData,
  VtkFieldData,
  VtkAlgorithm,
  VtkThresholdPoints,
  VtkReader,
  VtkPicking,
  VtkVolumeController,
  VtkShareDataSetRoot,
  VtkRegisterDataSet,
  VtkUseDataSet,
  VtkAnnotation,
  VtkAnnotations,
};
