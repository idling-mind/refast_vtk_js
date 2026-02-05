"""
Basic Triangle Example

This example demonstrates rendering a simple 3D triangle using the
refast_vtk_js extension.

Run with: python examples/basic_triangle.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Container, Heading, Text
from refast_vtk_js import (
    GeometryRepresentation,
    PointData,
    DataArray,
    PolyData,
    View,
)

# Create the Refast app with VTK extension
ui = RefastApp(
    title="VTK.js Basic Triangle",
)


@ui.page("/")
def home(ctx: Context):
    """Home page with a 3D triangle visualization."""
    # Triangle vertices: 3 points with x, y, z coordinates
    points = [
        0.0, 0.0, 0.0,    # Point 0: origin
        1.0, 0.0, 0.0,    # Point 1: right
        0.5, 1.0, 0.0,    # Point 2: top center
    ]

    # Color values for each point (for coloring by scalar)
    colors = [0.0, 0.5, 1.0]  # One value per point

    return Container(
        class_name="p-4 max-w-4xl mx-auto",
        children=[
            Heading("VTK.js 3D Triangle", level=1, class_name="mb-4"),
            Text(
                "This is a simple triangle rendered with VTK.js. "
                "You can rotate the view by dragging with the left mouse button.",
                class_name="mb-4 text-muted-foreground",
            ),
            View(
                background=[0.1, 0.15, 0.2],
                style={"width": "100%", "height": "400px"},
                children=[
                    GeometryRepresentation(
                        color_map_preset="Rainbow",
                        color_data_range=[0, 1],
                        property={
                            "edgeVisibility": True,
                            "edgeColor": [1, 1, 1],
                        },
                        children=[
                            PolyData(
                                points=points,
                                connectivity="triangles",
                                children=[
                                    PointData(
                                        children=[
                                            DataArray(
                                                name="colors",
                                                registration="setScalars",
                                                values=colors,
                                                number_of_components=1,
                                            )
                                        ]
                                    )
                                ],
                            )
                        ],
                    )
                ],
            ),
            Text(
                "Controls: Left-drag to rotate, Right-drag to zoom, Middle-drag to pan",
                class_name="mt-2 text-sm text-muted-foreground",
            ),
        ],
    )


# Create FastAPI app
app = FastAPI(title="VTK.js Triangle Demo")
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js Triangle Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
