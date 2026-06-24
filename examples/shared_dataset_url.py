"""
Shared Dataset URL Example

This example demonstrates loading a 3D model from a ZIP file via a URL
once and rendering it in three separate views using the data-sharing components:
ShareDataSetRoot, RegisterDataSet, and UseDataSet.

Run with: python examples/shared_dataset_url.py
Then open: http://localhost:8000
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from refast import Context, RefastApp
from refast.components import (
    Container,
    Heading,
    Text,
    ResizablePanelGroup,
    ResizablePanel,
    ResizableHandle,
)
from refast_vtk_js import (
    View,
    GeometryRepresentation,
    Reader,
    ShareDataSetRoot,
    RegisterDataSet,
    UseDataSet,
)

# Create the Refast app
ui = RefastApp(
    title="VTK.js Shared Dataset URL Example",
)

MODEL_URL = "/static-assets/space-shuttle-orbiter.obj"


@ui.page("/")
def home(ctx: Context):
    """Home page rendering the shared model in three views."""
    
    # Define a 3-way split dashboard layout
    panels = ResizablePanelGroup(
        direction="horizontal",
        class_name="border rounded-lg h-full",
        style={"width": "100%", "height": "calc(100vh - 10rem)"},
        children=[
            # Left View: Surface Representation
            ResizablePanel(
                min_size=20,
                default_size=33,
                children=[
                    Container(
                        class_name="relative h-full",
                        children=[
                            Text(
                                "Surface View (Solid)",
                                class_name="absolute top-2 left-2 z-10 bg-secondary px-2 py-1 rounded text-xs font-semibold text-foreground pointer-events-none border border-border shadow-sm",
                            ),
                            View(
                                id="view-surface",
                                background=[0.1, 0.1, 0.15],
                                sync_group="spaceship",
                                style={"width": "100%", "height": "100%"},
                                children=[
                                    GeometryRepresentation(
                                        property={
                                            "representation": 2,  # Surface
                                            "color": [0.2, 0.6, 1.0],  # Blue
                                            "opacity": 1.0,
                                        },
                                        children=[
                                            UseDataSet(dataset_id="shared-spaceship")
                                        ],
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            ),
            ResizableHandle(with_handle=True),
            
            # Middle View: Wireframe Representation
            ResizablePanel(
                min_size=20,
                default_size=34,
                children=[
                    Container(
                        class_name="relative h-full",
                        children=[
                            Text(
                                "Wireframe View",
                                class_name="absolute top-2 left-2 z-10 bg-secondary px-2 py-1 rounded text-xs font-semibold text-foreground pointer-events-none border border-border shadow-sm",
                            ),
                            View(
                                id="view-wireframe",
                                background=[0.1, 0.1, 0.15],
                                sync_group="spaceship",
                                style={"width": "100%", "height": "100%"},
                                children=[
                                    GeometryRepresentation(
                                        property={
                                            "representation": 1,  # Wireframe
                                            "color": [0.2, 1.0, 0.6],  # Greenish-Teal
                                            "opacity": 0.8,
                                        },
                                        children=[
                                            UseDataSet(dataset_id="shared-spaceship")
                                        ],
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            ),
            ResizableHandle(with_handle=True),
            
            # Right View: Point Cloud Representation
            ResizablePanel(
                min_size=20,
                default_size=33,
                children=[
                    Container(
                        class_name="relative h-full",
                        children=[
                            Text(
                                "Points View",
                                class_name="absolute top-2 left-2 z-10 bg-secondary px-2 py-1 rounded text-xs font-semibold text-foreground pointer-events-none border border-border shadow-sm",
                            ),
                            View(
                                id="view-points",
                                background=[0.1, 0.1, 0.15],
                                sync_group="spaceship",
                                style={"width": "100%", "height": "100%"},
                                children=[
                                    GeometryRepresentation(
                                        property={
                                            "representation": 0,  # Points
                                            "color": [1.0, 0.4, 0.4],  # Red-Orange
                                            "pointSize": 3.0,
                                        },
                                        children=[
                                            UseDataSet(dataset_id="shared-spaceship")
                                        ],
                                    )
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
    )

    return ShareDataSetRoot(
        children=[
            # Register the dataset under ShareDataSetRoot so any child view can use it.
            # This downloads the ZIP/OBJ only once and parses it in-memory.
            RegisterDataSet(
                dataset_id="shared-spaceship",
                children=[
                    Reader(
                        vtk_class="vtkOBJReader",
                        url=MODEL_URL,
                    )
                ],
            ),
            Container(
                class_name="p-4 mx-auto w-full h-screen flex flex-col gap-4 bg-background",
                children=[
                    Container(
                        children=[
                            Heading(
                                "VTK.js Shared Dataset via URL",
                                level=1,
                                class_name="mb-1 text-2xl font-bold tracking-tight text-foreground",
                            ),
                            Text(
                                "Demonstrates downloading a single 3D OBJ file packaged inside a ZIP once, "
                                "and displaying it across three views with synced cameras and different rendering representation modes (Solid, Wireframe, Points).",
                                class_name="text-sm text-muted-foreground",
                            ),
                        ],
                    ),
                    Container(
                        class_name="flex-1 min-h-0",
                        children=[panels],
                    ),
                ],
            ),
        ]
    )


# Create FastAPI application
app = FastAPI(title="VTK.js Shared Dataset Example")

# Mount the examples directory to serve space-shuttle-orbiter.obj
app.mount(
    "/static-assets",
    StaticFiles(directory=Path(__file__).parent),
    name="static-assets",
)

app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    print(f"Starting VTK.js Shared Dataset Demo on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    uvicorn.run(app, host="0.0.0.0", port=port)
