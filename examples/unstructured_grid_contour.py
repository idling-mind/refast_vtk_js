"""
PyVista Unstructured Grid Contour Example

This example shows how to:
1. Load a ``pyvista.UnstructuredGrid`` (placeholder included)
2. Compute an isocontour surface from a scalar field
3. Render the contour with refast_vtk_js

Run with: python examples/unstructured_grid_contour.py
Then open: http://localhost:8000
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Container, Heading, Text
from refast_vtk_js import DataArray, GeometryRepresentation, PointData, PolyData, View

try:
    import pyvista as pv
except ImportError as exc:  # pragma: no cover - example runtime guard
    raise ImportError(
        "This example requires pyvista. Install with: pip install pyvista"
    ) from exc


# Create the Refast app with VTK extension
ui = RefastApp(
    title="VTK.js Unstructured Grid Contour",
)


def load_unstructured_grid() -> pv.UnstructuredGrid:
    """Load your unstructured grid (replace placeholder with your real source)."""
    # Placeholder: replace this with your own dataset path or data source.
    # Example:
    # ugrid = pv.read("path/to/your_mesh.vtu")
    # return ugrid
    raise RuntimeError(
        "Set up `load_unstructured_grid()` with your file path (for example via pv.read)."
    )


def build_contour_payload(
    grid: pv.UnstructuredGrid,
    *,
    isovalue: float,
    scalar_name: str | None = None,
) -> dict[str, Any]:
    """
    Compute a contour and convert it to refast_vtk_js ``PolyData`` payload.

    Returns a dict with:
    - points: flat XYZ list
    - polys: polygon connectivity list
    - strips: strip connectivity list
    - scalars: point scalar values for coloring
    - scalar_range: [min, max] range used for color mapping
    - scalar_name: scalar array name used for contouring
    """
    available_point_arrays = list(grid.point_data.keys())
    if not available_point_arrays and scalar_name is None:
        raise ValueError(
            "No point-data scalar arrays found on the UnstructuredGrid. "
            "Specify `scalar_name` or add point scalars before contouring."
        )

    active_scalar_name = scalar_name or available_point_arrays[0]
    contour = grid.contour(isosurfaces=[isovalue], scalars=active_scalar_name)

    if contour.n_points == 0:
        raise ValueError(
            f"Contour is empty for scalar '{active_scalar_name}' at isovalue {isovalue}."
        )

    contour_scalars = contour.point_data.get(active_scalar_name)
    if contour_scalars is None:
        contour_scalars = contour.active_scalars

    if contour_scalars is None:
        contour_scalars = [isovalue] * contour.n_points

    scalar_values = (
        contour_scalars.tolist()
        if hasattr(contour_scalars, "tolist")
        else list(contour_scalars)
    )
    scalar_min = min(scalar_values)
    scalar_max = max(scalar_values)
    scalar_range = [scalar_min, scalar_max]

    # Avoid zero-span lookup table ranges for near-constant contour scalars.
    if scalar_min == scalar_max:
        delta = abs(scalar_min) * 0.01 if scalar_min != 0 else 1.0
        scalar_range = [scalar_min - delta, scalar_max + delta]

    return {
        "points": contour.points.ravel().tolist(),
        "polys": contour.faces.tolist() if contour.faces.size > 0 else None,
        "strips": contour.strips.tolist() if contour.strips.size > 0 else None,
        "scalars": scalar_values,
        "scalar_range": scalar_range,
        "scalar_name": active_scalar_name,
    }


@ui.page("/")
def home(ctx: Context):
    """Home page displaying contour extracted from an unstructured grid."""
    try:
        ugrid = load_unstructured_grid()

        # Choose an isovalue that makes sense for your scalar range.
        contour_data = build_contour_payload(
            ugrid,
            isovalue=0.5,
            scalar_name=None,
        )

        vtk_view = View(
            background=[0.07, 0.1, 0.14],
            style={"width": "100%", "height": "560px"},
            children=[
                GeometryRepresentation(
                    color_map_preset="Cool to Warm",
                    color_data_range=contour_data["scalar_range"],
                    mapper={
                        "scalarVisibility": True,
                        "interpolateScalarsBeforeMapping": True,
                        "useLookupTableScalarRange": True,
                    },
                    show_cube_axes=True,
                    cube_axes_style={"ticks": 6},
                    show_scalar_bar=True,
                    scalar_bar_title=True,
                    scalar_bar_style={"axisLabel": contour_data["scalar_name"]},
                    property={
                        "edgeVisibility": True,
                        "edgeColor": [0.9, 0.9, 0.9],
                        "opacity": 1.0,
                    },
                    children=[
                        PolyData(
                            points=contour_data["points"],
                            polys=contour_data["polys"],
                            strips=contour_data["strips"],
                            connectivity="manual",
                            children=[
                                PointData(
                                    children=[
                                        DataArray(
                                            name=contour_data["scalar_name"],
                                            registration="setScalars",
                                            values=contour_data["scalars"],
                                            number_of_components=1,
                                        )
                                    ]
                                )
                            ],
                        )
                    ],
                )
            ],
        )

        status = Text(
            "Contour rendered successfully. Use left-drag rotate, right-drag zoom, middle-drag pan.",
            class_name="mt-2 text-sm text-muted-foreground",
        )
    except Exception as exc:
        vtk_view = Container(
            class_name="rounded-md border border-destructive/40 bg-destructive/10 p-4",
            children=[
                Text(
                    "Could not render contour yet. Update load_unstructured_grid() first.",
                    class_name="font-medium",
                ),
                Text(str(exc), class_name="mt-2 text-sm text-muted-foreground"),
            ],
        )
        status = Text(
            "After setting your data source, reload the page to see the contour.",
            class_name="mt-2 text-sm text-muted-foreground",
        )

    return Container(
        class_name="p-4 max-w-5xl mx-auto",
        children=[
            Heading("VTK.js Contour from PyVista UnstructuredGrid", level=1, class_name="mb-3"),
            Text(
                "This demo computes a contour using PyVista and displays it with refast_vtk_js.",
                class_name="mb-4 text-muted-foreground",
            ),
            vtk_view,
            status,
        ],
    )


# Create FastAPI app
app = FastAPI(title="VTK.js Unstructured Grid Contour Demo")
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js Unstructured Grid Contour Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
