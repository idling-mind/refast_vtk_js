"""
Client-side ThresholdPoints Filter Example

This example demonstrates using the ThresholdPoints component to apply
scalar threshold-based clipping to a 3D sphere mesh entirely on the client
side in the browser.

Run with: python examples/threshold_points.py
Then open: http://localhost:8000
"""

import pyvista as pv
from fastapi import FastAPI
import uvicorn

from refast import Context, RefastApp
from refast.components import Button, Card, CardContent, Container, Grid, Heading, Slider, Text
from refast_vtk_js import (
    DataArray,
    GeometryRepresentation,
    PointData,
    PolyData,
    ThresholdPoints,
    View,
)

# Initialize Refast App
ui = RefastApp(
    title="VTK.js Client-side Threshold Points Demo",
)

# 1. Generate a sphere mesh using PyVista
sphere = pv.Sphere(radius=1.0, theta_resolution=32, phi_resolution=32)
sphere_points = sphere.points.ravel().tolist()
sphere_polys = sphere.faces.tolist()
# Create scalar field based on Z-coordinates ranging from -1.0 to 1.0
sphere_scalars = sphere.points[:, 2].tolist()

# 2. Store active filter state on the backend
current_operation = "Above"
current_value = 0.0

# 3. Define interactive callback functions

async def handle_slider_change(ctx: Context):
    global current_value
    current_value = ctx.event_data["value"][0]
    await update_filter(ctx)

async def handle_op_above(ctx: Context):
    global current_operation
    current_operation = "Above"
    # Highlight the active button
    await ctx.update_props("btn-above", {"variant": "default"})
    await ctx.update_props("btn-below", {"variant": "outline"})
    await update_filter(ctx)

async def handle_op_below(ctx: Context):
    global current_operation
    current_operation = "Below"
    # Highlight the active button
    await ctx.update_props("btn-above", {"variant": "outline"})
    await ctx.update_props("btn-below", {"variant": "default"})
    await update_filter(ctx)

async def update_filter(ctx: Context):
    """Send updated filter properties to the frontend ThresholdPoints component."""
    criterias = [
        {
            "array_name": "z_coord",
            "field_association": "PointData",
            "operation": current_operation,
            "value": current_value,
        }
    ]
    # Update ThresholdPoints criterias
    await ctx.update_props("thresh-filter", {"criterias": criterias})
    
    # Update text feedback
    op_symbol = "≥" if current_operation == "Above" else "≤"
    await ctx.update_props(
        "active-status",
        {"text": f"Active Filter: z_coord {op_symbol} {current_value:.2f}"}
    )


# 4. Define the UI Layout

@ui.page("/")
def home(ctx: Context):
    # Initial criteria values
    initial_criterias = [
        {
            "array_name": "z_coord",
            "field_association": "PointData",
            "operation": current_operation,
            "value": current_value,
        }
    ]

    return Container(
        class_name="p-6 max-w-6xl mx-auto space-y-6",
        children=[
            Heading(
                "Client-side Point Thresholding",
                level=1,
                class_name="text-3xl font-extrabold tracking-tight"
            ),
            Text(
                "This example runs the VTK.js ThresholdPoints filter inside your browser. "
                "Unlike backend clipping which regenerates meshes, this filter clips and threshold-filters "
                "the vertices in real time on the GPU/client.",
                class_name="text-muted-foreground",
            ),
            
            Grid(
                columns=3,
                gap=6,
                children=[
                    # Control panel card
                    Card(
                        class_name="col-span-1 h-fit",
                        children=[
                            CardContent(
                                class_name="p-4 space-y-6",
                                children=[
                                    Heading("Filter Controls", level=2, class_name="text-xl font-bold"),
                                    
                                    Container(
                                        class_name="space-y-2",
                                        children=[
                                            Text("Threshold Value", class_name="text-sm font-medium"),
                                            Slider(
                                                min=-0.95,
                                                max=0.95,
                                                step=0.05,
                                                default_value=[0.0],
                                                show_value=True,
                                                on_value_change=ctx.callback(handle_slider_change),
                                            ),
                                        ]
                                    ),
                                    
                                    Container(
                                        class_name="space-y-2",
                                        children=[
                                            Text("Operation Mode", class_name="text-sm font-medium"),
                                            Container(
                                                class_name="flex gap-2",
                                                children=[
                                                    Button(
                                                        "Keep Above (>=)",
                                                        id="btn-above",
                                                        variant="default",
                                                        on_click=ctx.callback(handle_op_above),
                                                        class_name="w-full",
                                                    ),
                                                    Button(
                                                        "Keep Below (<=)",
                                                        id="btn-below",
                                                        variant="outline",
                                                        on_click=ctx.callback(handle_op_below),
                                                        class_name="w-full",
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    
                                    Text(
                                        "Active Filter: z_coord ≥ 0.00",
                                        id="active-status",
                                        class_name="p-2 bg-muted rounded text-sm text-center font-mono block"
                                    ),
                                ]
                            )
                        ]
                    ),
                    
                    # 3D Viewport card
                    Card(
                        class_name="col-span-2",
                        children=[
                            CardContent(
                                class_name="p-4 space-y-4",
                                children=[
                                    View(
                                        id="vtk-view",
                                        background=[0.08, 0.1, 0.12],
                                        style={"width": "100%", "height": "500px"},
                                        children=[
                                            GeometryRepresentation(
                                                color_map_preset="Cool to Warm",
                                                color_data_range=[-1.0, 1.0],
                                                show_scalar_bar=True,
                                                scalar_bar_title="Z Coordinate",
                                                property={
                                                    "representation": 2, # Surface rendering
                                                    "edgeVisibility": True,
                                                    "edgeColor": [0.3, 0.3, 0.3],
                                                },
                                                children=[
                                                    ThresholdPoints(
                                                        id="thresh-filter",
                                                        criterias=initial_criterias,
                                                        children=[
                                                            PolyData(
                                                                points=sphere_points,
                                                                polys=sphere_polys,
                                                                connectivity="manual",
                                                                children=[
                                                                    PointData(
                                                                        children=[
                                                                            DataArray(
                                                                                name="z_coord",
                                                                                registration="setScalars",
                                                                                values=sphere_scalars,
                                                                                number_of_components=1,
                                                                            )
                                                                        ]
                                                                    )
                                                                ]
                                                            )
                                                        ]
                                                    )
                                                ]
                                            )
                                        ]
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# 5. Fast API setup and router inclusion
app = FastAPI(title="VTK.js Threshold Points Demo")
app.include_router(ui.router)

if __name__ == "__main__":
    print("Starting client-side ThresholdPoints demo...")
    print("Open http://127.0.0.1:9005 in your browser.")
    uvicorn.run(app, host="127.0.0.1", port=9005)
