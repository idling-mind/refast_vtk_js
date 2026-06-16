"""Refast extension for VTK.js

Provides React-VTK.js components for 3D visualization in Refast applications.
"""

from pathlib import Path

from refast.extensions import Extension

from .components import (
    Algorithm,
    AxesActor,
    CellData,
    DataArray,
    Dataset,
    FieldData,
    Geometry2DRepresentation,
    GeometryRepresentation,
    ImageData,
    MultiViewRoot,
    Picking,
    PointData,
    PolyData,
    Reader,
    RegisterDataSet,
    ShareDataSetRoot,
    SliceRepresentation,
    ThresholdPoints,
    UseDataSet,
    View,
    VolumeController,
    VolumeRepresentation,
)


class VtkExtension(Extension):
    """
    VTK.js extension for Refast.

    Provides 3D visualization components powered by react-vtk-js.

    Example:
        ```python
        from refast import RefastApp
        from refast_vtk_js import View, GeometryRepresentation, PolyData, VtkExtension

        ui = RefastApp(extensions=[VtkExtension()])

        @ui.page("/")
        def home(ctx):
            return View(
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

    For auto-discovery, install the package and it will be automatically loaded.
    """

    name = "refast_vtk_js"
    version = "0.1.0"
    description = "VTK.js 3D visualization components for Refast"

    # Static assets to load (relative to static_path)
    scripts = ["refast_vtk_js.js"]
    styles = []  # Add CSS files here if needed: ["refast_vtk_js.css"]

    @property
    def static_path(self) -> Path:
        """Path to the static assets directory."""
        return Path(__file__).parent / "static"

    @property
    def components(self) -> list:
        """List of Python component classes provided by this extension."""
        return [
            View,
            AxesActor,
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
            ThresholdPoints,
            Reader,
            Picking,
            VolumeController,
            ShareDataSetRoot,
            RegisterDataSet,
            UseDataSet,
        ]


__all__ = [
    # Extension
    "VtkExtension",
    # View components
    "View",
    "AxesActor",
    "MultiViewRoot",
    # Representation components
    "GeometryRepresentation",
    "Geometry2DRepresentation",
    "VolumeRepresentation",
    "SliceRepresentation",
    # Dataset components
    "PolyData",
    "ImageData",
    "Dataset",
    # Data array components
    "DataArray",
    "PointData",
    "CellData",
    "FieldData",
    # Algorithm & Reader
    "Algorithm",
    "ThresholdPoints",
    "Reader",
    # Interaction
    "Picking",
    "VolumeController",
    # Data sharing
    "ShareDataSetRoot",
    "RegisterDataSet",
    "UseDataSet",
]
