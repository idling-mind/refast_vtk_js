"""
Synced Multi-View Example

This example demonstrates camera synchronization between multiple VTK views.
Views that share the same `sync_group` will have their cameras linked —
rotating, panning, or zooming one view applies the same transformation to
every other view in the group.

Run with: python examples/sync_views.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Container, Heading, Text
from refast_vtk_js import (
    Algorithm,
    GeometryRepresentation,
    MultiViewRoot,
    View,
)

ui = RefastApp(
    title="VTK.js Synced Views",
)


@ui.page("/")
def home(ctx: Context):
    """Home page with synced multi-view 3D visualizations."""
    return Container(
        class_name="p-4 max-w-6xl mx-auto",
        children=[
            Heading("VTK.js Synced Multi-View", level=1, class_name="mb-2"),
            Text(
                "The left two views share sync_group='main' — interact with one "
                "and the other follows.  The right view has no sync group and "
                "moves independently.",
                class_name="mb-4 text-muted-foreground",
            ),
            MultiViewRoot(
                style={
                    "width": "100%",
                    "height": "600px",
                    "display": "grid",
                    "gridTemplateColumns": "1fr 1fr 1fr",
                    "gap": "4px",
                },
                children=[
                    # --- Synced view 1: Cone (blue) ---
                    View(
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
                    # --- Synced view 2: Sphere (red) ---
                    View(
                        background=[0.25, 0.15, 0.15],
                        sync_group="main",
                        style={"width": "100%", "height": "100%"},
                        children=[
                            GeometryRepresentation(
                                property={
                                    "color": [1.0, 0.3, 0.3],
                                    "edgeVisibility": True,
                                    "edgeColor": [0.4, 0.4, 0.4],
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
                    # --- Independent view: Cylinder (green) ---
                    View(
                        background=[0.15, 0.25, 0.15],
                        style={"width": "100%", "height": "100%"},
                        children=[
                            GeometryRepresentation(
                                property={
                                    "color": [0.3, 0.9, 0.4],
                                    "edgeVisibility": True,
                                    "edgeColor": [0.4, 0.4, 0.4],
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
            ),
            Text(
                "Controls: Left-drag to rotate, Right-drag to zoom, "
                "Middle-drag to pan.",
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
