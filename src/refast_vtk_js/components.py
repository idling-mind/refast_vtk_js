"""Component definitions for Refast extension for VTK.js.

This module provides Python wrappers for all React components from react-vtk-js.
These components allow you to create 3D visualizations in Refast applications.
"""

from typing import Any, Literal

from refast.components.base import Component


# ============================================================================
# View Components
# ============================================================================


class View(Component):
    """
    Main VTK view component that renders a 3D scene.

    This is the primary container for VTK visualizations. It combines
    OpenGLRenderWindow, RenderWindow, and Renderer functionality.

    Args:
        background: RGB or RGBA background color as 3-4 element list of floats (0-1)
        interactive: Whether the view is interactive (default: True)
        camera: Camera properties (position, focal_point, view_up, etc.)
        auto_reset_camera: Whether to auto-reset camera on data changes (default: True)
        interactor_settings: List of mouse interaction settings
        auto_center_of_rotation: Whether to auto-center rotation (default: True)
        style: CSS style properties for the container
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import View, GeometryRepresentation, PolyData

        View(
            background=[0.2, 0.3, 0.4],
            style={"width": "100%", "height": "400px"},
            children=[
                GeometryRepresentation(
                    children=[
                        PolyData(
                            points=[0, 0, 0, 1, 0, 0, 0.5, 1, 0],
                            connectivity="triangles"
                        )
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkView"

    def __init__(
        self,
        background: list[float] | None = None,
        interactive: bool = True,
        camera: dict[str, Any] | None = None,
        auto_reset_camera: bool = True,
        interactor_settings: list[dict[str, Any]] | None = None,
        auto_center_of_rotation: bool = True,
        style: dict[str, Any] | None = None,
        render_window_style: dict[str, Any] | None = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.background = background
        self.interactive = interactive
        self.camera = camera
        self.auto_reset_camera = auto_reset_camera
        self.interactor_settings = interactor_settings
        self.auto_center_of_rotation = auto_center_of_rotation
        self.style = style
        self.render_window_style = render_window_style

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "background": self.background,
                "interactive": self.interactive,
                "camera": self.camera,
                "auto_reset_camera": self.auto_reset_camera,
                "interactor_settings": self.interactor_settings,
                "auto_center_of_rotation": self.auto_center_of_rotation,
                "style": self.style,
                "render_window_style": self.render_window_style,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class MultiViewRoot(Component):
    """
    Container for multiple VTK views sharing the same OpenGL context.

    Use this when you need multiple synchronized views of the same or
    different data, sharing a single WebGL context for performance.

    Args:
        style: CSS style properties for the container
        render_window_style: CSS style for the render window
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import MultiViewRoot, View

        MultiViewRoot(
            style={"width": "100%", "height": "600px"},
            children=[
                View(background=[0.1, 0.1, 0.1]),
                View(background=[0.2, 0.2, 0.2]),
            ]
        )
        ```
    """

    component_type = "VtkMultiViewRoot"

    def __init__(
        self,
        style: dict[str, Any] | None = None,
        render_window_style: dict[str, Any] | None = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.style = style
        self.render_window_style = render_window_style

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "style": self.style,
                "render_window_style": self.render_window_style,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


# ============================================================================
# Representation Components
# ============================================================================


class GeometryRepresentation(Component):
    """
    Representation for rendering 3D geometry (surfaces, lines, points).

    This is the most common representation for polygon-based data like
    meshes, surfaces, and point clouds.

    Args:
        actor: Actor properties (visibility, position, scale, etc.)
        mapper: Mapper properties
        property: Surface property (color, opacity, representation, etc.)
        color_map_preset: Color map preset name (e.g., 'erdc_rainbow_bright')
        color_data_range: Data range for color mapping [min, max]
        show_cube_axes: Show/hide cube axes
        cube_axes_style: Style properties for cube axes
        show_scalar_bar: Show/hide scalar bar
        scalar_bar_title: Title for scalar bar
        scalar_bar_style: Style properties for scalar bar
        on_data_available: Callback when data becomes available
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import View, GeometryRepresentation, PolyData

        View(
            children=[
                GeometryRepresentation(
                    property={"color": [1, 0, 0], "opacity": 0.8},
                    children=[
                        PolyData(points=[...], polys=[...])
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkGeometryRepresentation"

    def __init__(
        self,
        actor: dict[str, Any] | None = None,
        mapper: dict[str, Any] | None = None,
        property: dict[str, Any] | None = None,
        color_map_preset: str = "erdc_rainbow_bright",
        color_data_range: list[float] | None = None,
        show_cube_axes: bool = False,
        cube_axes_style: dict[str, Any] | None = None,
        show_scalar_bar: bool = False,
        scalar_bar_title: bool = False,
        scalar_bar_style: dict[str, Any] | None = None,
        on_data_available: Any = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.actor = actor
        self.mapper = mapper
        self.property = property
        self.color_map_preset = color_map_preset
        self.color_data_range = color_data_range
        self.show_cube_axes = show_cube_axes
        self.cube_axes_style = cube_axes_style
        self.show_scalar_bar = show_scalar_bar
        self.scalar_bar_title = scalar_bar_title
        self.scalar_bar_style = scalar_bar_style
        self.on_data_available = on_data_available

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "actor": self.actor,
                "mapper": self.mapper,
                "property": self.property,
                "color_map_preset": self.color_map_preset,
                "color_data_range": self.color_data_range,
                "show_cube_axes": self.show_cube_axes,
                "cube_axes_style": self.cube_axes_style,
                "show_scalar_bar": self.show_scalar_bar,
                "scalar_bar_title": self.scalar_bar_title,
                "scalar_bar_style": self.scalar_bar_style,
                "on_data_available": (
                    self.on_data_available.serialize() if self.on_data_available else None
                ),
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class Geometry2DRepresentation(Component):
    """
    Representation for rendering 2D geometry overlays.

    Used for rendering 2D overlays like annotations, markers, or
    2D plots on top of 3D views.

    Args:
        actor: Actor2D properties
        mapper: Mapper2D properties
        property: Property2D settings
        color_map_preset: Color map preset name
        color_data_range: Data range for color mapping [min, max]
        transform_coordinate: Coordinate system for input data
        on_data_available: Callback when data becomes available
        id: Component ID
        class_name: CSS classes
    """

    component_type = "VtkGeometry2DRepresentation"

    def __init__(
        self,
        actor: dict[str, Any] | None = None,
        mapper: dict[str, Any] | None = None,
        property: dict[str, Any] | None = None,
        color_map_preset: str = "erdc_rainbow_bright",
        color_data_range: list[float] | None = None,
        transform_coordinate: dict[str, Any] | None = None,
        on_data_available: Any = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.actor = actor
        self.mapper = mapper
        self.property = property
        self.color_map_preset = color_map_preset
        self.color_data_range = color_data_range
        self.transform_coordinate = transform_coordinate
        self.on_data_available = on_data_available

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "actor": self.actor,
                "mapper": self.mapper,
                "property": self.property,
                "color_map_preset": self.color_map_preset,
                "color_data_range": self.color_data_range,
                "transform_coordinate": self.transform_coordinate,
                "on_data_available": (
                    self.on_data_available.serialize() if self.on_data_available else None
                ),
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class VolumeRepresentation(Component):
    """
    Representation for volume rendering of 3D image data.

    Used for visualizing volumetric datasets like CT scans, MRI, or
    any 3D scalar field.

    Args:
        actor: Volume actor properties
        mapper: Volume mapper properties
        property: Volume property (transfer functions, shading, etc.)
        color_map_preset: Color map preset name
        color_data_range: Data range for color mapping ('auto' or [min, max])
        on_data_available: Callback when data becomes available
        on_data_changed: Callback when data changes
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import View, VolumeRepresentation, ImageData, DataArray, PointData

        View(
            children=[
                VolumeRepresentation(
                    color_map_preset="Cool to Warm",
                    children=[
                        ImageData(
                            dimensions=[10, 10, 10],
                            spacing=[1, 1, 1],
                            children=[
                                PointData(
                                    children=[
                                        DataArray(
                                            registration="setScalars",
                                            values=[...]
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkVolumeRepresentation"

    def __init__(
        self,
        actor: dict[str, Any] | None = None,
        mapper: dict[str, Any] | None = None,
        property: dict[str, Any] | None = None,
        color_map_preset: str = "erdc_rainbow_bright",
        color_data_range: str | list[float] = "auto",
        on_data_available: Any = None,
        on_data_changed: Any = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.actor = actor
        self.mapper = mapper
        self.property = property
        self.color_map_preset = color_map_preset
        self.color_data_range = color_data_range
        self.on_data_available = on_data_available
        self.on_data_changed = on_data_changed

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "actor": self.actor,
                "mapper": self.mapper,
                "property": self.property,
                "color_map_preset": self.color_map_preset,
                "color_data_range": self.color_data_range,
                "on_data_available": (
                    self.on_data_available.serialize() if self.on_data_available else None
                ),
                "on_data_changed": (
                    self.on_data_changed.serialize() if self.on_data_changed else None
                ),
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class SliceRepresentation(Component):
    """
    Representation for displaying 2D slices of 3D image data.

    Used for viewing cross-sections of volumetric data along
    different axes (i, j, k or x, y, z).

    Args:
        actor: ImageSlice actor properties
        mapper: ImageMapper properties
        property: ImageProperty settings
        color_map_preset: Color map preset name
        color_data_range: Data range for color mapping ('auto' or [min, max])
        i_slice: Slice index along i axis
        j_slice: Slice index along j axis
        k_slice: Slice index along k axis
        x_slice: Slice position along x axis
        y_slice: Slice position along y axis
        z_slice: Slice position along z axis
        on_data_available: Callback when data becomes available
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import View, SliceRepresentation, ImageData

        View(
            children=[
                SliceRepresentation(
                    k_slice=50,  # Show slice at z=50
                    color_map_preset="Grayscale",
                    children=[
                        ImageData(dimensions=[100, 100, 100], ...)
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkSliceRepresentation"

    def __init__(
        self,
        actor: dict[str, Any] | None = None,
        mapper: dict[str, Any] | None = None,
        property: dict[str, Any] | None = None,
        color_map_preset: str = "Grayscale",
        color_data_range: str | list[float] = "auto",
        i_slice: int | None = None,
        j_slice: int | None = None,
        k_slice: int | None = None,
        x_slice: float | None = None,
        y_slice: float | None = None,
        z_slice: float | None = None,
        on_data_available: Any = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.actor = actor
        self.mapper = mapper
        self.property = property
        self.color_map_preset = color_map_preset
        self.color_data_range = color_data_range
        self.i_slice = i_slice
        self.j_slice = j_slice
        self.k_slice = k_slice
        self.x_slice = x_slice
        self.y_slice = y_slice
        self.z_slice = z_slice
        self.on_data_available = on_data_available

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "actor": self.actor,
                "mapper": self.mapper,
                "property": self.property,
                "color_map_preset": self.color_map_preset,
                "color_data_range": self.color_data_range,
                "i_slice": self.i_slice,
                "j_slice": self.j_slice,
                "k_slice": self.k_slice,
                "x_slice": self.x_slice,
                "y_slice": self.y_slice,
                "z_slice": self.z_slice,
                "on_data_available": (
                    self.on_data_available.serialize() if self.on_data_available else None
                ),
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


# ============================================================================
# Dataset Components
# ============================================================================


class PolyData(Component):
    """
    Polygonal dataset component for geometry representation.

    Defines polygon-based geometry using points and cell connectivity
    (vertices, lines, polygons, triangle strips).

    Args:
        points: XYZ coordinates as flat list [x1,y1,z1, x2,y2,z2, ...] or
               numpy-encoded array {"bvals": base64, "dtype": str, "shape": list}
        verts: Vertex cell connectivity
        lines: Line cell connectivity
        polys: Polygon cell connectivity
        strips: Triangle strip cell connectivity
        connectivity: Auto-connectivity type ('manual', 'points', 'triangles', 'strips')
        port: Downstream connection port (default: 0)
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        # Triangle with 3 vertices
        PolyData(
            points=[0, 0, 0, 1, 0, 0, 0.5, 1, 0],
            connectivity="triangles"
        )

        # Point cloud
        PolyData(
            points=[0, 0, 0, 1, 1, 1, 2, 2, 2],
            connectivity="points"
        )

        # Manual connectivity
        PolyData(
            points=[0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0],
            polys=[4, 0, 1, 2, 3]  # Quad with 4 vertices
        )
        ```
    """

    component_type = "VtkPolyData"

    def __init__(
        self,
        points: list[float] | dict[str, Any] | None = None,
        verts: list[int] | dict[str, Any] | None = None,
        lines: list[int] | dict[str, Any] | None = None,
        polys: list[int] | dict[str, Any] | None = None,
        strips: list[int] | dict[str, Any] | None = None,
        connectivity: Literal["manual", "points", "triangles", "strips"] = "manual",
        port: int = 0,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.points = points
        self.verts = verts
        self.lines = lines
        self.polys = polys
        self.strips = strips
        self.connectivity = connectivity
        self.port = port

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "points": self.points,
                "verts": self.verts,
                "lines": self.lines,
                "polys": self.polys,
                "strips": self.strips,
                "connectivity": self.connectivity,
                "port": self.port,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class ImageData(Component):
    """
    Regular grid dataset component for volume/image data.

    Defines a regular 3D grid with uniform spacing for volumetric data.

    Args:
        dimensions: Grid dimensions [nx, ny, nz]
        spacing: Grid spacing [dx, dy, dz]
        origin: Grid origin [x0, y0, z0]
        direction: Orientation matrix (9 values, column-major)
        port: Downstream connection port (default: 0)
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import ImageData, PointData, DataArray

        ImageData(
            dimensions=[50, 50, 50],
            spacing=[0.1, 0.1, 0.1],
            origin=[0, 0, 0],
            children=[
                PointData(
                    children=[
                        DataArray(
                            registration="setScalars",
                            values=scalar_values,  # 50*50*50 values
                            number_of_components=1
                        )
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkImageData"

    def __init__(
        self,
        dimensions: list[int] | None = None,
        spacing: list[float] | None = None,
        origin: list[float] | None = None,
        direction: list[float] | None = None,
        port: int = 0,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.dimensions = dimensions
        self.spacing = spacing
        self.origin = origin
        self.direction = direction
        self.port = port

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "dimensions": self.dimensions,
                "spacing": self.spacing,
                "origin": self.origin,
                "direction": self.direction,
                "port": self.port,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class Dataset(Component):
    """
    Generic dataset wrapper for passing VTK objects directly.

    Use when you have a pre-constructed vtkObject that you want
    to visualize.

    Args:
        dataset: The VTK dataset object (serialized)
        id: Component ID
        class_name: CSS classes
    """

    component_type = "VtkDataset"

    def __init__(
        self,
        dataset: Any = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.dataset = dataset

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "dataset": self.dataset,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


# ============================================================================
# Data Array Components
# ============================================================================


class DataArray(Component):
    """
    Data array component for attaching scalar/vector data to datasets.

    Used to attach field data (scalars, vectors, colors, etc.) to
    points or cells of a dataset.

    Args:
        name: Name of the data array
        type: Typed array type ('Float32Array', 'Int32Array', etc.)
        values: Array values as list or numpy-encoded array
        number_of_components: Number of components per tuple (1 for scalars, 3 for vectors)
        registration: Method to call on field data ('addArray', 'setScalars', 'setVectors', etc.)
        range: Data value range [min, max]
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        # Scalar data for coloring
        DataArray(
            name="temperature",
            registration="setScalars",
            values=[0.0, 0.5, 1.0, ...],
            number_of_components=1
        )

        # Vector data (normals)
        DataArray(
            name="normals",
            registration="setNormals",
            values=[0, 0, 1, 0, 0, 1, ...],  # Flat list of nx,ny,nz
            number_of_components=3
        )
        ```
    """

    component_type = "VtkDataArray"

    def __init__(
        self,
        name: str = "scalars",
        type: str = "Float32Array",
        values: list[float | int] | dict[str, Any] | None = None,
        number_of_components: int = 1,
        registration: str = "addArray",
        range: list[float] | None = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.name = name
        self.type = type
        self.values = values
        self.number_of_components = number_of_components
        self.registration = registration
        self.range = range

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "name": self.name,
                "type": self.type,
                "values": self.values,
                "number_of_components": self.number_of_components,
                "registration": self.registration,
                "range": self.range,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class PointData(Component):
    """
    Container for point-associated data arrays.

    Use as a container for DataArray components that should be
    associated with points (vertices) of the dataset.

    Args:
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        PolyData(
            points=[...],
            children=[
                PointData(
                    children=[
                        DataArray(name="scalars", values=[...]),
                        DataArray(name="normals", values=[...], number_of_components=3)
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkPointData"

    def __init__(
        self,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class CellData(Component):
    """
    Container for cell-associated data arrays.

    Use as a container for DataArray components that should be
    associated with cells (faces, lines, etc.) of the dataset.

    Args:
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        PolyData(
            points=[...],
            polys=[...],
            children=[
                CellData(
                    children=[
                        DataArray(name="cellColors", values=[...])
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkCellData"

    def __init__(
        self,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class FieldData(Component):
    """
    Container for field data arrays (not associated with points or cells).

    Args:
        id: Component ID
        class_name: CSS classes
    """

    component_type = "VtkFieldData"

    def __init__(
        self,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


# ============================================================================
# Algorithm & Reader Components
# ============================================================================


class Algorithm(Component):
    """
    Generic VTK algorithm component.

    Wrapper for any VTK algorithm/filter that can process data.
    The algorithm is specified by its vtkClass name.

    Args:
        vtk_class: VTK class name (e.g., 'vtkConeSource', 'vtkSphereSource')
        state: Initial state/properties to set on the algorithm
        port: Output port number for downstream connection
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import View, GeometryRepresentation, Algorithm

        View(
            children=[
                GeometryRepresentation(
                    children=[
                        Algorithm(
                            vtk_class="vtkConeSource",
                            state={
                                "height": 2.0,
                                "radius": 0.5,
                                "resolution": 60
                            }
                        )
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkAlgorithm"

    def __init__(
        self,
        vtk_class: str = "",
        state: dict[str, Any] | None = None,
        port: int = 0,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.vtk_class = vtk_class
        self.state = state
        self.port = port

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "vtk_class": self.vtk_class,
                "state": self.state,
                "port": self.port,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class Reader(Component):
    """
    VTK file reader component.

    Reads data from files/URLs and produces VTK objects.
    Supports various file formats depending on the vtkClass used.

    Args:
        vtk_class: VTK reader class name (e.g., 'vtkOBJReader', 'vtkSTLReader')
        url: URL to fetch data from (must be CORS-accessible)
        url_options: Options passed to reader's setUrl() method
        array_buffer: ArrayBuffer containing data to parse
        base64_array_buffer: Base64-encoded ArrayBuffer
        text: Text content to parse
        port: Output port for downstream connection
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        from refast_vtk_js import View, GeometryRepresentation, Reader

        View(
            children=[
                GeometryRepresentation(
                    children=[
                        Reader(
                            vtk_class="vtkOBJReader",
                            url="https://example.com/model.obj"
                        )
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkReader"

    def __init__(
        self,
        vtk_class: str = "",
        url: str | None = None,
        url_options: dict[str, Any] | None = None,
        array_buffer: Any = None,
        base64_array_buffer: str | None = None,
        text: str | None = None,
        port: int = 0,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.vtk_class = vtk_class
        self.url = url
        self.url_options = url_options
        self.array_buffer = array_buffer
        self.base64_array_buffer = base64_array_buffer
        self.text = text
        self.port = port

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "vtk_class": self.vtk_class,
                "url": self.url,
                "url_options": self.url_options,
                "array_buffer": self.array_buffer,
                "base64_array_buffer": self.base64_array_buffer,
                "text": self.text,
                "port": self.port,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


# ============================================================================
# Interaction Components
# ============================================================================


class Picking(Component):
    """
    Mouse picking component for interactive selection.

    Enables picking/selection of actors in the view via mouse
    events (click, hover, pointer down/up).

    Args:
        enabled: Whether picking is enabled (default: True)
        on_hover: Callback when hovering over an actor
        on_click: Callback when clicking an actor
        on_pointer_down: Callback when pointer pressed on actor
        on_pointer_up: Callback when pointer released on actor
        pointer_size: Tolerance for selection (pixels)
        on_hover_debounce_wait: Debounce wait for hover events (ms)
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        def handle_click(ctx):
            selection = ctx.event.data
            print(f"Clicked: {selection.get('worldPosition')}")

        View(
            children=[
                Picking(
                    on_click=ctx.callback(handle_click),
                    pointer_size=5
                ),
                GeometryRepresentation(...)
            ]
        )
        ```
    """

    component_type = "VtkPicking"

    def __init__(
        self,
        enabled: bool = True,
        on_hover: Any = None,
        on_click: Any = None,
        on_pointer_down: Any = None,
        on_pointer_up: Any = None,
        pointer_size: int = 0,
        on_hover_debounce_wait: int = 4,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.enabled = enabled
        self.on_hover = on_hover
        self.on_click = on_click
        self.on_pointer_down = on_pointer_down
        self.on_pointer_up = on_pointer_up
        self.pointer_size = pointer_size
        self.on_hover_debounce_wait = on_hover_debounce_wait

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "enabled": self.enabled,
                "on_hover": self.on_hover.serialize() if self.on_hover else None,
                "on_click": self.on_click.serialize() if self.on_click else None,
                "on_pointer_down": (
                    self.on_pointer_down.serialize() if self.on_pointer_down else None
                ),
                "on_pointer_up": (
                    self.on_pointer_up.serialize() if self.on_pointer_up else None
                ),
                "pointer_size": self.pointer_size,
                "on_hover_debounce_wait": self.on_hover_debounce_wait,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class VolumeController(Component):
    """
    UI controller for volume rendering.

    Provides an interactive widget for adjusting volume rendering
    transfer functions.

    Args:
        size: Widget size [width, height] in pixels
        rescale_color_map: Whether to rescale color map on data change
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        VolumeRepresentation(
            children=[
                VolumeController(size=[400, 150]),
                ImageData(...)
            ]
        )
        ```
    """

    component_type = "VtkVolumeController"

    def __init__(
        self,
        size: list[int] | None = None,
        rescale_color_map: bool = True,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.size = size
        self.rescale_color_map = rescale_color_map

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "size": self.size,
                "rescale_color_map": self.rescale_color_map,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


# ============================================================================
# Data Sharing Components
# ============================================================================


class ShareDataSetRoot(Component):
    """
    Root component for sharing datasets between representations.

    Enables efficient sharing of data between multiple views/representations
    without duplicating the data.

    Args:
        id: Component ID
        class_name: CSS classes

    Example:
        ```python
        ShareDataSetRoot(
            children=[
                RegisterDataSet(
                    id="shared-mesh",
                    children=[PolyData(points=[...])]
                ),
                View(
                    children=[
                        GeometryRepresentation(
                            children=[UseDataSet(id="shared-mesh")]
                        )
                    ]
                ),
                View(
                    children=[
                        GeometryRepresentation(
                            property={"color": [1, 0, 0]},
                            children=[UseDataSet(id="shared-mesh")]
                        )
                    ]
                )
            ]
        )
        ```
    """

    component_type = "VtkShareDataSetRoot"

    def __init__(
        self,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class RegisterDataSet(Component):
    """
    Register a dataset for sharing with UseDataSet components.

    Args:
        dataset_id: Unique ID for the shared dataset (required)
        id: Component ID
        class_name: CSS classes
    """

    component_type = "VtkRegisterDataSet"

    def __init__(
        self,
        dataset_id: str,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.dataset_id = dataset_id

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "dataset_id": self.dataset_id,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }


class UseDataSet(Component):
    """
    Use a dataset registered with RegisterDataSet.

    Args:
        dataset_id: ID of the shared dataset to use (required)
        port: Input port number (default: 0)
        id: Component ID
        class_name: CSS classes
    """

    component_type = "VtkUseDataSet"

    def __init__(
        self,
        dataset_id: str,
        port: int = 0,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.dataset_id = dataset_id
        self.port = port

    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "dataset_id": self.dataset_id,
                "port": self.port,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }
