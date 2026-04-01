"""
Geometry Representation Options Example

Comprehensive demo for GeometryRepresentation options in refast-vtk-js.

What this example covers:
- show_cube_axes and cube_axes_style
- show_scalar_bar, scalar_bar_title, and scalar_bar_style
- color_map_preset and color_data_range
- actor, mapper, and property configuration
- Runtime prop updates via buttons (using ctx.update_props)

Run with: python examples/geometry_representation_options.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Button, Container, Heading, Text
from refast_vtk_js import (
    Algorithm,
    DataArray,
    GeometryRepresentation,
    PointData,
    PolyData,
    View,
)

ui = RefastApp(title="VTK.js GeometryRepresentation Options")


def build_colored_cube_polydata() -> PolyData:
    """Create a cube mesh with point scalars for scalar bar/color map demos."""
    points = [
        -0.5,
        -0.5,
        -0.5,
        0.5,
        -0.5,
        -0.5,
        0.5,
        0.5,
        -0.5,
        -0.5,
        0.5,
        -0.5,
        -0.5,
        -0.5,
        0.5,
        0.5,
        -0.5,
        0.5,
        0.5,
        0.5,
        0.5,
        -0.5,
        0.5,
        0.5,
    ]

    # 12 triangles (two per face), VTK-style: [3, i0, i1, i2, 3, ...]
    polys = [
        3,
        0,
        1,
        2,
        3,
        0,
        2,
        3,
        3,
        4,
        5,
        6,
        3,
        4,
        6,
        7,
        3,
        0,
        1,
        5,
        3,
        0,
        5,
        4,
        3,
        3,
        2,
        6,
        3,
        3,
        6,
        7,
        3,
        0,
        3,
        7,
        3,
        0,
        7,
        4,
        3,
        1,
        2,
        6,
        3,
        1,
        6,
        5,
    ]

    # Scalar values per point (lower to upper along z axis)
    scalars = [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]

    return PolyData(
        points=points,
        polys=polys,
        children=[
            PointData(
                children=[
                    DataArray(
                        name="elevation",
                        registration="setScalars",
                        values=scalars,
                        number_of_components=1,
                        range=[0.0, 1.0],
                    )
                ]
            )
        ],
    )


async def set_preset_rainbow(ctx: Context):
    """Set rainbow color map preset."""
    await ctx.update_props("geom-main", {"color_map_preset": "erdc_rainbow_bright"})


async def set_preset_cool_to_warm(ctx: Context):
    """Set cool-to-warm color map preset."""
    await ctx.update_props("geom-main", {"color_map_preset": "Cool to Warm"})


async def set_cube_axes_on(ctx: Context):
    """Enable cube axes."""
    await ctx.update_props("geom-main", {"show_cube_axes": True})


async def set_cube_axes_off(ctx: Context):
    """Disable cube axes."""
    await ctx.update_props("geom-main", {"show_cube_axes": False})


async def set_scalar_bar_on(ctx: Context):
    """Enable scalar bar and title."""
    await ctx.update_props(
        "geom-main",
        {
            "show_scalar_bar": True,
            "scalar_bar_title": True,
        },
    )


async def set_scalar_bar_off(ctx: Context):
    """Disable scalar bar."""
    await ctx.update_props("geom-main", {"show_scalar_bar": False})


async def set_scalar_bar_light_labels(ctx: Context):
    """Set scalar bar title/tick labels to bright colors for dark backgrounds."""
    await ctx.update_props(
        "geom-main",
        {
            "scalar_bar_style": {
                "axisTextStyle": {
                    "fontColor": "#ffe082",
                    "fontFamily": "Arial",
                    "fontSize": 20,
                    "fontStyle": "bold",
                },
                "tickTextStyle": {
                    "fontColor": "#f5f5f5",
                    "fontFamily": "Arial",
                    "fontSize": 14,
                },
            }
        },
    )


async def set_scalar_bar_warm_labels(ctx: Context):
    """Set scalar bar title/tick labels to warm accent colors."""
    await ctx.update_props(
        "geom-main",
        {
            "scalar_bar_style": {
                "axisTextStyle": {
                    "fontColor": "#ff6f61",
                    "fontFamily": "Arial",
                    "fontSize": 20,
                    "fontStyle": "bold",
                },
                "tickTextStyle": {
                    "fontColor": "#ffd166",
                    "fontFamily": "Arial",
                    "fontSize": 14,
                },
            }
        },
    )


async def set_surface_with_edges(ctx: Context):
    """Set surface representation with edge visibility."""
    await ctx.update_props(
        "geom-main",
        {
            "property": {
                "representation": 2,
                "edgeVisibility": True,
                "edgeColor": [0.1, 0.1, 0.1],
                "opacity": 1.0,
            }
        },
    )


async def set_wireframe(ctx: Context):
    """Set wireframe representation."""
    await ctx.update_props(
        "geom-main",
        {
            "property": {
                "representation": 1,
                "color": [0.95, 0.95, 0.95],
                "lineWidth": 2.0,
                "opacity": 1.0,
            }
        },
    )


@ui.page("/")
def home(ctx: Context):
    """Page showing GeometryRepresentation options in action."""
    return Container(
        class_name="p-4 max-w-6xl mx-auto space-y-4",
        children=[
            Heading("GeometryRepresentation Options", level=1),
            Text(
                "This scene demonstrates scalar coloring, scalar bar, cube axes, "
                "mapper controls, actor transforms, and property modes.",
                class_name="text-muted-foreground",
            ),
            Container(
                class_name="flex flex-wrap gap-2",
                children=[
                    Button(
                        "Preset: Rainbow",
                        on_click=ctx.callback(set_preset_rainbow),
                    ),
                    Button(
                        "Preset: Cool to Warm",
                        on_click=ctx.callback(set_preset_cool_to_warm),
                    ),
                    Button(
                        "Cube Axes ON",
                        on_click=ctx.callback(set_cube_axes_on),
                    ),
                    Button(
                        "Cube Axes OFF",
                        on_click=ctx.callback(set_cube_axes_off),
                    ),
                    Button(
                        "Scalar Bar ON",
                        on_click=ctx.callback(set_scalar_bar_on),
                    ),
                    Button(
                        "Scalar Bar OFF",
                        on_click=ctx.callback(set_scalar_bar_off),
                    ),
                    Button(
                        "Scalar Bar: Light Labels",
                        on_click=ctx.callback(set_scalar_bar_light_labels),
                    ),
                    Button(
                        "Scalar Bar: Warm Labels",
                        on_click=ctx.callback(set_scalar_bar_warm_labels),
                    ),
                    Button(
                        "Surface + Edges",
                        on_click=ctx.callback(set_surface_with_edges),
                    ),
                    Button(
                        "Wireframe",
                        on_click=ctx.callback(set_wireframe),
                    ),
                ],
            ),
            View(
                id="geometry-options-view",
                background=[0.08, 0.1, 0.13],
                auto_reset_camera=False,
                style={"width": "100%", "height": "620px"},
                children=[
                    GeometryRepresentation(
                        id="geom-main",
                        actor={
                            "position": [-1.1, 0.0, 0.0],
                            "scale": [1.0, 1.0, 1.0],
                            "visibility": True,
                        },
                        mapper={
                            "scalarVisibility": True,
                            "interpolateScalarsBeforeMapping": True,
                            "useLookupTableScalarRange": True,
                        },
                        property={
                            "representation": 2,
                            "edgeVisibility": True,
                            "edgeColor": [0.1, 0.1, 0.1],
                            "opacity": 1.0,
                        },
                        color_map_preset="erdc_rainbow_bright",
                        color_data_range=[0.0, 1.0],
                        show_cube_axes=True,
                        cube_axes_style={"ticks": 4},
                        show_scalar_bar=True,
                        scalar_bar_title="elevation",
                        scalar_bar_style={
                            "axisTextStyle": {
                                "fontColor": "#ffe082",
                                "fontFamily": "Arial",
                                "fontSize": 20,
                                "fontStyle": "bold",
                            },
                            "tickTextStyle": {
                                "fontColor": "#f5f5f5",
                                "fontFamily": "Arial",
                                "fontSize": 14,
                            },
                        },
                        children=[build_colored_cube_polydata()],
                    ),
                    GeometryRepresentation(
                        actor={
                            "position": [1.1, 0.0, 0.0],
                            "scale": [1.0, 1.0, 1.0],
                        },
                        mapper={
                            "scalarVisibility": False,
                        },
                        property={
                            "representation": 1,
                            "color": [0.85, 0.9, 1.0],
                            "lineWidth": 2.0,
                            "opacity": 1.0,
                        },
                        children=[
                            Algorithm(
                                vtk_class="vtkSphereSource",
                                state={
                                    "thetaResolution": 32,
                                    "phiResolution": 32,
                                    "radius": 0.65,
                                },
                            )
                        ],
                    ),
                ],
            ),
            Text(
                "Left mesh: scalar-mapped cube with cube axes and scalar bar. "
                "Right mesh: actor + property focused wireframe sphere.",
                class_name="text-sm text-muted-foreground",
            ),
            Text(
                "Tip: Use the buttons above to update GeometryRepresentation props at runtime.",
                class_name="text-sm text-muted-foreground",
            ),
        ],
    )


app = FastAPI(title="VTK.js GeometryRepresentation Options Demo")
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js GeometryRepresentation Options Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
