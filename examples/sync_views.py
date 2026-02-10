"""
Synced Views Example

This example demonstrates camera synchronization between VTK views using
the `sync_group` prop.  Views that share the same sync_group will have
their cameras linked — rotating, panning, or zooming one view applies the
same transformation to every other view in the group.

sync_group works with standalone Views placed anywhere in the DOM — there
is no requirement for MultiViewRoot.  You can freely wrap Views inside
any Refast layout component (Container, Row, Column, etc.) and they will
still sync as long as they share a sync_group value.

Run with: python examples/sync_views.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import (
    Container,
    Heading,
    Text,
    ResizablePanelGroup,
    ResizablePanel,
    ResizableHandle,
    ToggleGroup,
    ToggleGroupItem,
)
from refast_vtk_js import (
    Algorithm,
    GeometryRepresentation,
    View,
)

ui = RefastApp(
    title="VTK.js Synced Views",
)


async def sync_views(ctx: Context, view: str):
    """Sync Views"""
    view = view.replace("toggle-", "view-")
    await ctx.update_props(
        target_id=view,
        props={"sync_group": None if not ctx.event_data["value"] else "main"},
    )


@ui.page("/")
def home(ctx: Context):
    """Home page with synced multi-view 3D visualizations."""
    return Container(
        class_name="p-4 mx-auto",
        children=[
            Container(
                [
                    Heading("VTK.js Synced Views", level=1, class_name="mb-2"),
                    Text(
                        "This example demonstrates camera synchronization between VTK views using the "
                        "`sync_group` prop. Views that share the same sync_group will have their cameras linked — "
                        "rotating, panning, or zooming one view applies the same transformation to every other view in the group.",
                        class_name="mb-4 text-muted-foreground",
                    ),
                ],
                class_name="mb-4",
            ),
            # ---- Resizable panels layout ----
            ResizablePanelGroup(
                direction="horizontal",
                class_name="border rounded-lg h-full",
                style={"width": "100%", "height": "calc(100vh - 10rem)"},
                children=[
                    ResizablePanel(
                        min_size=20,
                        default_size=50,
                        children=[
                            Container(
                                class_name="relative h-full",
                                children=[
                                    Text(
                                        "Cone",
                                        class_name="absolute top-2 left-2 z-10 bg-card/80 px-2 py-1 rounded text-sm text-white font-medium pointer-events-none",
                                    ),
                                    Container(
                                        [
                                            ToggleGroup(
                                                default_value="toggle-cone",
                                                type="single",
                                                children=[
                                                    ToggleGroupItem(
                                                        name="toggle-cone",
                                                        icon="refresh-cw",
                                                    )
                                                ],
                                                on_value_change=ctx.callback(
                                                    sync_views, view="toggle-cone"
                                                ),
                                            )
                                        ],
                                        class_name="absolute p-2 right-2 z-10",
                                    ),
                                    View(
                                        id="view-cone",
                                        background=[0.15, 0.15, 0.25],
                                        sync_group="main",
                                        style={"width": "100%", "height": "100%"},
                                        children=[
                                            GeometryRepresentation(
                                                property={
                                                    "color": [0.2, 0.6, 1.0],
                                                    "edgeVisibility": True,
                                                    "edgeColor": [0.4, 0.4, 0.4],
                                                },
                                                children=[
                                                    Algorithm(
                                                        vtk_class="vtkConeSource",
                                                        state={
                                                            "resolution": 32,
                                                            "radius": 0.5,
                                                            "height": 1.0,
                                                            "capping": True,
                                                        },
                                                    )
                                                ],
                                            ),
                                        ],
                                    ),
                                ],
                            )
                        ],
                        class_name="bg-card",
                    ),
                    ResizableHandle(with_handle=True),
                    ResizablePanel(
                        min_size=20,
                        default_size=50,
                        children=[
                            ResizablePanelGroup(
                                direction="vertical",
                                children=[
                                    ResizablePanel(
                                        min_size=20,
                                        default_size=70,
                                        children=[
                                            Container(
                                                class_name="relative h-full",
                                                children=[
                                                    Text(
                                                        "Sphere",
                                                        class_name="absolute top-2 left-2 z-10 bg-card/80 px-2 py-1 rounded text-sm text-white font-medium pointer-events-none",
                                                    ),
                                                    Container(
                                                        [
                                                            ToggleGroup(
                                                                default_value="toggle-sphere",
                                                                type="single",
                                                                children=[
                                                                    ToggleGroupItem(
                                                                        name="toggle-sphere",
                                                                        icon="refresh-cw",
                                                                    )
                                                                ],
                                                                on_value_change=ctx.callback(
                                                                    sync_views,
                                                                    view="toggle-sphere",
                                                                ),
                                                            )
                                                        ],
                                                        class_name="absolute p-2 right-2 z-10",
                                                    ),
                                                    View(
                                                        id="view-sphere",
                                                        background=[0.25, 0.15, 0.15],
                                                        sync_group="main",
                                                        style={
                                                            "width": "100%",
                                                            "height": "100%",
                                                        },
                                                        children=[
                                                            GeometryRepresentation(
                                                                property={
                                                                    "color": [
                                                                        1.0,
                                                                        0.3,
                                                                        0.3,
                                                                    ],
                                                                    "edgeVisibility": True,
                                                                    "edgeColor": [
                                                                        0.4,
                                                                        0.4,
                                                                        0.4,
                                                                    ],
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
                                                        ],
                                                    ),
                                                ],
                                            )
                                        ],
                                        class_name="bg-card",
                                    ),
                                    ResizableHandle(with_handle=True),
                                    ResizablePanel(
                                        min_size=20,
                                        default_size=30,
                                        children=[
                                            Container(
                                                class_name="relative h-full",
                                                children=[
                                                    Text(
                                                        "Cylinder",
                                                        class_name="absolute top-2 left-2 z-10 bg-card/80 px-2 py-1 rounded text-sm text-white font-medium pointer-events-none",
                                                    ),
                                                    Container(
                                                        [
                                                            ToggleGroup(
                                                                type="single",
                                                                children=[
                                                                    ToggleGroupItem(
                                                                        name="toggle-cylinder",
                                                                        icon="refresh-cw",
                                                                    )
                                                                ],
                                                                on_value_change=ctx.callback(
                                                                    sync_views,
                                                                    view="toggle-cylinder",
                                                                ),
                                                            )
                                                        ],
                                                        class_name="absolute p-2 right-2 z-10",
                                                    ),
                                                    View(
                                                        id="view-cylinder",
                                                        background=[0.15, 0.25, 0.15],
                                                        style={
                                                            "width": "100%",
                                                            "height": "100%",
                                                        },
                                                        children=[
                                                            GeometryRepresentation(
                                                                property={
                                                                    "color": [
                                                                        0.3,
                                                                        0.9,
                                                                        0.4,
                                                                    ],
                                                                    "edgeVisibility": True,
                                                                    "edgeColor": [
                                                                        0.4,
                                                                        0.4,
                                                                        0.4,
                                                                    ],
                                                                },
                                                                children=[
                                                                    Algorithm(
                                                                        vtk_class="vtkCylinderSource",
                                                                        state={
                                                                            "resolution": 32,
                                                                            "radius": 0.4,
                                                                            "height": 1.0,
                                                                        },
                                                                    )
                                                                ],
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            )
                                        ],
                                        class_name="bg-card",
                                    ),
                                ],
                                style={"height": "100%", "width": "100%"},
                            )
                        ],
                        class_name="bg-card",
                    ),
                ],
            ),
            Text(
                "Controls: Left-drag to rotate, Right-drag to zoom, "
                "Middle-drag to pan, Scroll to zoom to mouse position.",
                class_name="mt-2 text-sm text-muted-foreground",
            ),
        ],
    )


app = FastAPI(title="VTK.js Synced Views Demo")
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js Synced Views Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
