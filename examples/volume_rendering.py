"""
Volume Rendering Example

This example demonstrates volume rendering with VTK.js, loading
a 3D image dataset and displaying it with volume rendering.

Run with: python examples/volume_rendering.py
Then open: http://localhost:8000
"""

from fastapi import FastAPI

from refast import Context, RefastApp
from refast.components import Container, Heading, Text
from refast_vtk_js import (
    DataArray,
    ImageData,
    PointData,
    View,
    VolumeController,
    VolumeRepresentation,
)

# Create the Refast app with VTK extension
ui = RefastApp(
    title="VTK.js Volume Rendering",
)


# Generate a simple 3D synthetic dataset
def generate_sphere_volume():
    """Generate a 3D volume with a sphere."""
    import math

    dimensions = [32, 32, 32]
    spacing = [1.0, 1.0, 1.0]
    origin = [0.0, 0.0, 0.0]
    center = [16, 16, 16]
    radius = 12

    scalars = []
    for z in range(dimensions[2]):
        for y in range(dimensions[1]):
            for x in range(dimensions[0]):
                dx = x - center[0]
                dy = y - center[1]
                dz = z - center[2]
                distance = math.sqrt(dx * dx + dy * dy + dz * dz)

                # Value based on distance from center
                if distance <= radius:
                    value = int(255 * (1 - distance / radius))
                else:
                    value = 0
                scalars.append(value)

    return dimensions, spacing, origin, scalars


@ui.page("/")
def home(ctx: Context):
    """Home page with volume rendering."""
    dimensions, spacing, origin, scalars = generate_sphere_volume()

    return Container(
        class_name="p-4 max-w-4xl mx-auto",
        children=[
            Heading("VTK.js Volume Rendering", level=1, class_name="mb-4"),
            Text(
                "This example shows volume rendering of a synthetic 3D sphere dataset. "
                "Use the controller to adjust the transfer function.",
                class_name="mb-4 text-muted-foreground",
            ),
            View(
                background=[0.0, 0.0, 0.0],
                style={"width": "100%", "height": "500px"},
                children=[
                    VolumeRepresentation(
                        children=[
                            VolumeController(rescale_color_map=True),
                            ImageData(
                                dimensions=dimensions,
                                spacing=spacing,
                                origin=origin,
                                direction=[1, 0, 0, 0, 1, 0, 0, 0, 1],
                                children=[
                                    PointData(
                                        children=[
                                            DataArray(
                                                name="scalars",
                                                registration="setScalars",
                                                values=scalars,
                                                number_of_components=1,
                                            )
                                        ]
                                    )
                                ],
                            ),
                        ]
                    )
                ],
            ),
            Text(
                "Volume rendering uses ray casting to display the 3D density field. "
                "The VolumeController widget allows interactive transfer function editing.",
                class_name="mt-2 text-sm text-muted-foreground",
            ),
        ],
    )


# Create FastAPI app
app = FastAPI(title="VTK.js Volume Demo")
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn

    print("Starting VTK.js Volume Rendering Demo...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
