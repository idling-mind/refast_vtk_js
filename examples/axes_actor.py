"""
AxesActor Example

Demonstrates a fixed-in-window orientation marker with axis annotation,
alongside runtime toggles for marker mode, corner, recenter, and inversion.

Run with: python examples/axes_actor.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Button, Container, Heading, Text
from refast_vtk_js import Algorithm, AxesActor, GeometryRepresentation, View

ui = RefastApp(title="VTK.js AxesActor Example")


async def set_recenter_on(ctx: Context):
    """Enable AxesActor recenter option."""
    await ctx.update_props("axes-actor", {"recenter": True})


async def set_recenter_off(ctx: Context):
    """Disable AxesActor recenter option."""
    await ctx.update_props("axes-actor", {"recenter": False})


async def set_x_invert_on(ctx: Context):
    """Enable X-axis inversion."""
    await ctx.update_props("axes-actor", {"x_axis_invert": True})


async def set_x_invert_off(ctx: Context):
    """Disable X-axis inversion."""
    await ctx.update_props("axes-actor", {"x_axis_invert": False})


async def set_y_invert_on(ctx: Context):
    """Enable Y-axis inversion."""
    await ctx.update_props("axes-actor", {"y_axis_invert": True})


async def set_y_invert_off(ctx: Context):
    """Disable Y-axis inversion."""
    await ctx.update_props("axes-actor", {"y_axis_invert": False})


async def set_z_invert_on(ctx: Context):
    """Enable Z-axis inversion."""
    await ctx.update_props("axes-actor", {"z_axis_invert": True})


async def set_z_invert_off(ctx: Context):
    """Disable Z-axis inversion."""
    await ctx.update_props("axes-actor", {"z_axis_invert": False})


async def set_fixed_marker_on(ctx: Context):
    """Enable fixed-in-window marker mode."""
    await ctx.update_props("axes-actor", {"fixed_in_window": True})


async def set_fixed_marker_off(ctx: Context):
    """Disable fixed-in-window marker mode (world actor mode)."""
    await ctx.update_props("axes-actor", {"fixed_in_window": False})


async def set_labels_on(ctx: Context):
    """Enable axis annotations."""
    await ctx.update_props(
        "axes-actor",
        {
            "axis_labels_enabled": True,
            "axis_labels": {
                "x_plus": "+X",
                "x_minus": "-X",
                "y_plus": "+Y",
                "y_minus": "-Y",
                "z_plus": "+Z",
                "z_minus": "-Z",
            },
        },
    )


async def set_labels_off(ctx: Context):
    """Disable axis annotations (show triad only)."""
    await ctx.update_props("axes-actor", {"axis_labels_enabled": False})


async def set_corner_top_right(ctx: Context):
    """Place marker in top-right corner."""
    await ctx.update_props("axes-actor", {"marker_corner": "TOP_RIGHT"})


async def set_corner_bottom_left(ctx: Context):
    """Place marker in bottom-left corner."""
    await ctx.update_props("axes-actor", {"marker_corner": "BOTTOM_LEFT"})


@ui.page("/")
def home(ctx: Context):
    """Render AxesActor demo page."""
    return Container(
        class_name="p-4 max-w-6xl mx-auto space-y-4",
        children=[
            Heading("VTK.js AxesActor", level=1),
            Text(
                "AxesActor supports fixed marker mode and labeled orientation annotation.",
                class_name="text-muted-foreground",
            ),
            Container(
                class_name="flex flex-wrap gap-2",
                children=[
                    Button("Fixed marker ON", on_click=ctx.callback(set_fixed_marker_on)),
                    Button("Fixed marker OFF", on_click=ctx.callback(set_fixed_marker_off)),
                    Button("Labels ON", on_click=ctx.callback(set_labels_on)),
                    Button("Labels OFF", on_click=ctx.callback(set_labels_off)),
                    Button("Corner TOP_RIGHT", on_click=ctx.callback(set_corner_top_right)),
                    Button("Corner BOTTOM_LEFT", on_click=ctx.callback(set_corner_bottom_left)),
                    Button("Recenter ON", on_click=ctx.callback(set_recenter_on)),
                    Button("Recenter OFF", on_click=ctx.callback(set_recenter_off)),
                    Button("X invert ON", on_click=ctx.callback(set_x_invert_on)),
                    Button("X invert OFF", on_click=ctx.callback(set_x_invert_off)),
                    Button("Y invert ON", on_click=ctx.callback(set_y_invert_on)),
                    Button("Y invert OFF", on_click=ctx.callback(set_y_invert_off)),
                    Button("Z invert ON", on_click=ctx.callback(set_z_invert_on)),
                    Button("Z invert OFF", on_click=ctx.callback(set_z_invert_off)),
                ],
            ),
            View(
                background=[0.2, 0.3, 0.4],
                style={"width": "100%", "height": "620px"},
                children=[
                    AxesActor(
                        id="axes-actor",
                        fixed_in_window=True,
                        marker_corner="BOTTOM_LEFT",
                        marker_viewport_size=0.18,
                        marker_min_pixel_size=64,
                        marker_max_pixel_size=180,
                        axis_labels_enabled=True,
                        axis_labels={
                            "x_plus": "+X",
                            "x_minus": "-X",
                            "y_plus": "+Y",
                            "y_minus": "-Y",
                            "z_plus": "+Z",
                            "z_minus": "-Z",
                        },
                        axis_label_style={
                            "font_color": "#f8fafc",
                            "font_size": "14px",
                            "font_weight": 700,
                        },
                        recenter=True,
                        x_axis_invert=False,
                        y_axis_invert=False,
                        z_axis_invert=False,
                    ),
                    GeometryRepresentation(
                        property={
                            "color": [0.95, 0.95, 0.95],
                            "opacity": 0.8,
                        },
                        children=[
                            Algorithm(
                                vtk_class="vtkConeSource",
                                state={
                                    "height": 1.5,
                                    "radius": 0.45,
                                    "resolution": 72,
                                },
                            )
                        ],
                    ),
                ],
            ),
        ],
    )


app = FastAPI(title="VTK.js AxesActor Example")
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js AxesActor example...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
