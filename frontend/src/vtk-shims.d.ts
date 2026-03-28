declare module '@kitware/vtk.js/Rendering/Core/CubeAxesActor' {
  const vtkCubeAxesActor: {
    newInstance: (initialValues?: Record<string, unknown>) => any;
  };
  export default vtkCubeAxesActor;
}

declare module 'react-vtk-js/dist/esm/core/contexts' {
  export function useRendererContext(): {
    get: () => any;
    requestRender: () => void;
  };

  export function useRepresentationContext(): {
    getActor: () => any;
    getMapper: () => any;
    onDataAvailable: (cb: () => void) => (() => void) | void;
    onDataChanged: (cb: () => void) => (() => void) | void;
  };
}