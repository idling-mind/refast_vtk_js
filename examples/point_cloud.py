"""
Point Cloud Example

This example demonstrates rendering a 3D point cloud using the
refast_vtk_js extension.

Run with: python examples/point_cloud.py
Then open: http://localhost:8000
"""
import asyncio
import math
import colorsys
import random
from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Container, Heading, Text, Button
from refast_vtk_js import (
    DataArray,
    GeometryRepresentation,
    PointData,
    PolyData,
    View,
)

# Create the Refast app with VTK extension
ui = RefastApp(
    title="VTK.js Point Cloud",
)

async def add_data(ctx: Context):
    """Callback to add more points following the spiral pattern and matching colors."""
    # Add 100 points that follow the same spiral style used initially
    for i in range(100):
        theta = random.uniform(0, 8 * math.pi)
        radius = 1
        x = math.cos(theta) * radius + random.uniform(-0.05, 0.05)
        y = math.sin(theta) * radius + random.uniform(-0.05, 0.05)
        z = random.uniform(-1, 1)
        await ctx.append_prop("point-cloud-polydata", "points", [x, y, z])
        # Color follows the angular position for a rainbow-like hue
        hue = (z + 1) / 2  # Normalize z to [0, 1] for hue
        await ctx.append_prop("point-colors", "values", hue)
        await asyncio.sleep(0.2)  # Faster streaming for a smooth effect


@ui.page("/")
def home(ctx: Context):
    """Home page with a 3D point cloud visualization."""
    # Generate a colorful cylindrical point cloud
    points: list[float] = []
    colors: list[float] = []

    return Container(
        class_name="p-4 max-w-4xl mx-auto",
        children=[
            Heading("VTK.js 3D Point Cloud", level=1, class_name="mb-4"),
            Text(
                "This example shows a colorful cylindrical point cloud."
                " Click the button to stream more points that follow the same cylindrical pattern," 
                " each added point will carry a matching rainbow color.",
                class_name="mb-4 text-muted-foreground",
            ),
            Button("Stream data", class_name="w-full my-4", on_click=ctx.callback(add_data)),
            View(
                background=[0.1, 0.15, 0.2],
                style={"width": "100%", "height": "500px"},
                children=[
                    GeometryRepresentation(
                        color_map_preset="Viridis",
                        color_data_range=[0, 1],
                        property={
                            "pointSize": 6.0,
                            "opacity": 1.0,
                        },
                        children=[
                            PolyData(
                                id="point-cloud-polydata",
                                points=points,
                                connectivity="points",
                                children=[
                                    PointData(
                                        children=[
                                            DataArray(
                                                id="point-colors",
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
app = FastAPI(title="VTK.js Point Cloud Demo")
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js Point Cloud Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
