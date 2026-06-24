"""
VTK.js Annotations and Dragging Example

This example demonstrates:
1. Adding single Annotations (`Annotation`) and plural Annotations (`Annotations`).
2. Drawing connecting lines from 3D points to offset annotation cards.
3. Enabling user-draggable annotation cards that update their 3D coordinates.
4. Customizing line colors, widths, and background colors.
5. Capturing real-time drag-end events on the Python server.

Run with: python examples/annotations_demo.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Container, Heading, Text, Column
from refast_vtk_js import (
    Algorithm,
    GeometryRepresentation,
    View,
    Annotation,
    Annotations,
)

VIEW_CONTROLS = [
    {"button": 2, "action": "Rotate"},
    {"button": 2, "action": "Zoom", "shift": True},
    {"button": 2, "action": "Pan", "control": True},
    {
        "button": 1,
        "action": "ZoomToMouse",
        "control": True,
        "scrollEnabled": True,
    },
    {"button": 3, "action": "Rotate"},
    {"button": 3, "action": "Zoom", "shift": True},
    {"button": 3, "action": "Pan", "control": True},
]

# Create the Refast app with VTK extension
ui = RefastApp(
    title="VTK.js Annotations & Dragging",
)


async def handle_annotation_drag(ctx: Context):
    """Callback triggered when the singular Annotation card is dragged and released."""
    pos = ctx.event_data.get("cardPosition")
    if pos:
        formatted_pos = f"Sphere Peak Card moved to: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]"
        print(formatted_pos)
        await ctx.update_text("annotation-info", formatted_pos)


async def handle_annotations_drag(ctx: Context):
    """Callback triggered when one of the plural Annotations items is dragged and released."""
    idx = ctx.event_data.get("index")
    pos = ctx.event_data.get("cardPosition")
    if pos:
        formatted_pos = f"Annotations Item {idx} Card moved to: [{pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}]"
        print(formatted_pos)
        await ctx.update_text("annotations-info", formatted_pos)


@ui.page("/")
def home(ctx: Context):
    """Home page visualizing a sphere and interactive annotations."""
    # Plural annotations items pointing to the left and right sides of the sphere
    annotations_items = [
        {
            "position": [-0.5, 0.0, 0.0],
            "text": "Left Side\n(Emerald Line)",
            "color": "#ffffff",
            "bg_color": "rgba(16, 185, 129, 0.9)",  # Emerald bg
            "anchor": "right-center",
        },
        {
            "position": [0.5, 0.0, 0.0],
            "text": "Right Side\n(Emerald Line)",
            "color": "#ffffff",
            "bg_color": "rgba(16, 185, 129, 0.9)",  # Emerald bg
            "anchor": "left-center",
        },
    ]

    return Container(
        class_name="p-6 max-w-5xl mx-auto flex flex-col gap-4",
        children=[
            Heading("VTK.js Draggable Annotations", level=1, class_name="text-3xl font-bold"),
            Text(
                "This example demonstrates interactive 3D annotations. "
                "You can drag the cards around in 3D space. When offset, "
                "connecting lines are drawn from the target 3D point to the card.",
                class_name="text-muted-foreground",
            ),
            View(
                id="vtk-view",
                background=[0.08, 0.1, 0.15],
                style={"width": "100%", "height": "500px"},
                auto_reset_camera=True,
                interactor_settings=VIEW_CONTROLS,
                children=[
                    # A 3D Sphere at the center (0,0,0) with radius 0.5
                    GeometryRepresentation(
                        property={
                            "color": [0.3, 0.4, 0.5],
                            "edgeVisibility": True,
                            "edgeColor": [0.5, 0.6, 0.7],
                            "opacity": 0.4,
                        },
                        children=[
                            Algorithm(
                                vtk_class="vtkSphereSource",
                                state={
                                    "thetaResolution": 24,
                                    "phiResolution": 24,
                                    "radius": 0.5,
                                },
                            )
                        ],
                    ),
                    # 1. Singular draggable Annotation at the sphere peak with an initial offset, line, and bottom-center anchor
                    Annotation(
                        position=[0.0, 0.5, 0.0],
                        card_position=[0.25, 0.75, 0.25],
                        show_line=True,
                        line_color="#3b82f6",  # Blue line
                        line_width=2.5,
                        draggable=True,
                        on_card_position_change=ctx.callback(handle_annotation_drag),
                        anchor="bottom-center",
                        children=[
                            Container(
                                class_name="bg-white border-2 border-blue-500 rounded px-2 py-1 shadow-lg text-black text-xs font-semibold select-none",
                                children=[
                                    Text("Sphere Peak (Blue Line)"),
                                    Text("Drag me in 3D!", class_name="text-[10px] text-blue-600 font-medium"),
                                ],
                            )
                        ],
                    ),
                    # 2. Singular draggable Annotation at the sphere base with an initial offset, red line, and top-center anchor
                    Annotation(
                        position=[0.0, -0.5, 0.0],
                        card_position=[0.0, -0.75, 0.0],
                        show_line=True,
                        line_color="#ef4444",  # Red line
                        line_width=2.5,
                        draggable=True,
                        on_card_position_change=ctx.callback(handle_annotation_drag),
                        anchor="top-center",
                        children=[
                            Container(
                                class_name="bg-slate-900 border border-slate-700 text-white rounded px-2 py-1 text-xs select-none shadow-md",
                                children=[
                                    Text("Sphere Base (Red Line, Top Anchored)"),
                                ],
                            )
                        ],
                    ),
                    # 3. Plural draggable Annotations (Left & Right sides)
                    Annotations(
                        items=annotations_items,
                        show_line=True,
                        line_color="#10b981",  # Emerald line
                        line_width=2.0,
                        draggable=True,
                        on_card_position_change=ctx.callback(handle_annotations_drag),
                    ),
                ],
            ),
            Column(
                class_name="bg-slate-900 border border-slate-800 rounded p-4 gap-2",
                children=[
                    Heading("Callback Console Logs", level=3, class_name="text-sm font-semibold text-slate-400"),
                    Text(
                        "No events received yet",
                        id="annotation-info",
                        class_name="text-xs font-mono text-blue-400",
                    ),
                    Text(
                        "No events received yet",
                        id="annotations-info",
                        class_name="text-xs font-mono text-emerald-400",
                    ),
                ],
            ),
        ],
    )


# Create FastAPI app
app = FastAPI(title="VTK.js Annotations & Dragging Demo")
app.include_router(ui.router)


if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js Annotations & Dragging Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
