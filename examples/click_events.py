"""
VTK.js Click Events Example

This example demonstrates how to use the `Picking` component to receive
click events from the VTK view. The Python callback prints the selection
info to the server console and attempts to update an on-page `Text`
component with the clicked world coordinates.

Run with: python examples/click_events.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Container, Heading, Text, Column
from refast_vtk_js import (
    Algorithm,
    DataArray,
    GeometryRepresentation,
    PointData,
    PolyData,
    Picking,
    View,
)

# Create the Refast app with VTK extension
ui = RefastApp(
    title="VTK.js Click Events",
)


async def handle_click(ctx: Context):
    """Callback to handle click events from the Picking component."""
    # Get the selection info from the event
    selection = ctx.event_data.get("selection", {})
    print("Selection received in server callback:", selection)

    # Extract world position if available
    world_pos = selection.get("worldPosition")
    if world_pos:
        world_pos_str = f"Clicked at world position: {world_pos}"
        print(world_pos_str)
        await ctx.update_text("click-info", world_pos_str)
    else:
        print("No world position in selection data.")

    sphere = Algorithm(
        vtk_class="vtkSphereSource",
        state={
            "center": world_pos if world_pos else [0, 0, 0],
            "radius": 0.01,
        },
    )
    sphere_view = GeometryRepresentation(children=[sphere])
    await ctx.append("vtk-view", sphere_view)


@ui.page("/")
def home(ctx: Context):
    """Home page with a 3D triangle and picking enabled."""
    # Triangle vertices
    points = [
        0.0,
        0.0,
        0.0,  # Point 0
        1.0,
        0.0,
        0.0,  # Point 1
        0.5,
        1.0,
        0.0,  # Point 2
    ]

    # Colors (scalars) for the points
    colors = [0.0, 0.5, 1.0]

    return Container(
        class_name="p-4 max-w-4xl mx-auto",
        children=[
            Heading("VTK.js Click Events", level=1, class_name="mb-4"),
            Container(
                [
                    Text(
                        "Click on the triangle in the view to see the selection printed in the server console."
                        " The selection world position will also be shown below (if supported by your Refast installation).",
                        class_name="text-muted-foreground",
                    ),
                ],
                class_name="mb-4",
            ),
            View(
                id="vtk-view",
                background=[0.1, 0.15, 0.2],
                style={"width": "100%", "height": "500px"},
                auto_reset_camera=False,
                children=[
                    # Register picking before geometry so it receives events
                    Picking(on_click=ctx.callback(handle_click), pointer_size=5),
                    GeometryRepresentation(
                        id="main-repr",
                        color_map_preset="Rainbow",
                        color_data_range=[0, 1],
                        property={
                            "edgeVisibility": True,
                            "edgeColor": [1, 1, 1],
                        },
                        children=[
                            PolyData(
                                id="triangle-polydata",
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
                    ),
                ],
            ),
            Column(
                [
                    Text(
                        "Controls: Left-drag to rotate, Right-drag to zoom, Middle-drag to pan",
                        class_name="mt-2 text-sm text-muted-foreground w-full",
                    ),
                    Text(
                        "No clicks yet",
                        id="click-info",
                        class_name="mt-4 text-sm text-muted-foreground w-full",
                    ),
                ]
            ),
        ],
    )


# Create FastAPI app
app = FastAPI(title="VTK.js Click Events Demo")
app.include_router(ui.router)


if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js Click Events Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
