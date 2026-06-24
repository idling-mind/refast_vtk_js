# refast-vtk-js

3D visualization extension for Refast powered by [react-vtk-js](https://github.com/Kitware/react-vtk-js).

A [Refast](https://github.com/idling-mind/refast) extension that provides VTK.js components for interactive 3D visualization in web applications.

## Features

- **View Components**: `View`, `MultiViewRoot` for creating 3D scenes
- **Representations**: `GeometryRepresentation`, `VolumeRepresentation`, `SliceRepresentation` for different visualization modes
- **Data Components**: `PolyData`, `ImageData`, `DataArray` for defining geometry and data
- **Algorithms**: `Algorithm`, `Reader` for data processing and file loading
- **Interaction**: `Picking` for mouse-based selection
- **Data Sharing**: `ShareDataSetRoot`, `RegisterDataSet`, `UseDataSet` for efficient data reuse

## Installation

```bash
pip install refast-vtk-js
```

## Usage

### Basic 3D Triangle

```python
from fastapi import FastAPI
from refast import RefastApp, Context
from refast.components import Container
from refast_vtk_js import View, GeometryRepresentation, PolyData

ui = RefastApp(title="VTK.js Demo")


@ui.page("/")
def home(ctx: Context):
    return Container(
        children=[
            View(
                background=[0.2, 0.3, 0.4],
                style={"width": "100%", "height": "400px"},
                children=[
                    GeometryRepresentation(
                        property={"color": [1, 0, 0]},
                        children=[
                            PolyData(
                                points=[0, 0, 0, 1, 0, 0, 0.5, 1, 0],
                                connectivity="triangles"
                            )
                        ]
                    )
                ]
            )
        ]
    )


app = FastAPI()
app.include_router(ui.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Using VTK Algorithms (Cone, Sphere, etc.)

```python
from refast_vtk_js import View, GeometryRepresentation, Algorithm

View(
    style={"width": "100%", "height": "400px"},
    children=[
        GeometryRepresentation(
            children=[
                Algorithm(
                    vtk_class="vtkConeSource",
                    state={
                        "height": 2.0,
                        "radius": 0.5,
                        "resolution": 60
                    }
                )
            ]
        )
    ]
)
```

### Volume Rendering

```python
from refast_vtk_js import View, VolumeRepresentation, ImageData, PointData, DataArray

# Create a 10x10x10 volume with scalar data
dimensions = [10, 10, 10]
values = [i / 1000 for i in range(10 * 10 * 10)]  # Scalar values

View(
    style={"width": "100%", "height": "400px"},
    children=[
        VolumeRepresentation(
            color_map_preset="Cool to Warm",
            children=[
                ImageData(
                    dimensions=dimensions,
                    spacing=[1, 1, 1],
                    origin=[0, 0, 0],
                    children=[
                        PointData(
                            children=[
                                DataArray(
                                    registration="setScalars",
                                    values=values,
                                    number_of_components=1
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)
```

### Loading 3D Models from URL

```python
from refast_vtk_js import View, GeometryRepresentation, Reader

View(
    style={"width": "100%", "height": "400px"},
    children=[
        GeometryRepresentation(
            children=[
                Reader(
                    vtk_class="vtkOBJReader",
                    url="https://example.com/model.obj"
                )
            ]
        )
    ]
)
```

### Interactive Picking

```python
from refast_vtk_js import View, GeometryRepresentation, PolyData, Picking

async def handle_click(ctx):
    selection = ctx.event_data.get("selection", {})
    world_pos = selection.get("worldPosition")
    print(f"Clicked at world position: {world_pos}")

View(
    style={"width": "100%", "height": "400px"},
    children=[
        Picking(
            on_click=ctx.callback(handle_click),
            pointer_size=5
        ),
        GeometryRepresentation(
            children=[
                PolyData(
                    points=[0, 0, 0, 1, 0, 0, 0.5, 1, 0],
                    connectivity="triangles"
                )
            ]
        )
    ]
)
```

### Sharing Data Between Views

```python
from refast_vtk_js import (
    ShareDataSetRoot, RegisterDataSet, UseDataSet,
    View, GeometryRepresentation, PolyData
)

ShareDataSetRoot(
    children=[
        # Register the shared data
        RegisterDataSet(
            dataset_id="shared-mesh",
            children=[
                PolyData(
                    points=[0, 0, 0, 1, 0, 0, 0.5, 1, 0],
                    connectivity="triangles"
                )
            ]
        ),
        # First view
        View(
            style={"width": "50%", "height": "300px"},
            children=[
                GeometryRepresentation(
                    property={"color": [1, 0, 0]},
                    children=[UseDataSet(dataset_id="shared-mesh")]
                )
            ]
        ),
        # Second view using same data
        View(
            style={"width": "50%", "height": "300px"},
            children=[
                GeometryRepresentation(
                    property={"color": [0, 0, 1]},
                    children=[UseDataSet(dataset_id="shared-mesh")]
                )
            ]
        )
    ]
)
```

### Draggable Annotations with Lines

You can add interactive 3D annotations (either singular or plural) that display HTML cards anchored at 3D world coordinates. If `draggable=True` is set, cards can be moved in screen space, and their updated coordinates will be unprojected back into 3D world space. Fired release events can update state via Python callbacks.

```python
from refast.components import Container, Text
from refast_vtk_js import View, Annotation, Annotations

async def handle_annotation_drag(ctx):
    pos = ctx.event_data.get("cardPosition")
    print(f"Annotation moved to: {pos}")

View(
    children=[
        # 1. Singular Annotation with custom Refast HTML children and a blue connecting line
        Annotation(
            position=[0.0, 0.5, 0.0],
            card_position=[0.25, 0.75, 0.25],
            show_line=True,
            line_color="#3b82f6",
            line_width=2.0,
            draggable=True,
            on_card_position_change=ctx.callback(handle_annotation_drag),
            anchor="bottom-center",
            bg_color="white",
            children=[
                Container(
                    class_name="bg-white border rounded p-2 text-black text-xs font-semibold",
                    children=[Text("Peak Annotation")],
                )
            ]
        ),
        # 2. Plural Annotations with simple text labels
        Annotations(
            items=[
                {
                    "position": [-0.5, 0.0, 0.0],
                    "text": "Left Annotation",
                    "anchor": "right-center",
                    "bg_color": "rgba(16, 185, 129, 0.9)",
                }
            ],
            show_line=True,
            line_color="#10b981",
            draggable=True,
        )
    ]
)
```

## Available Components

### View Components
- `View` - Main 3D view container
- `MultiViewRoot` - Container for multiple synchronized views

### Annotation Components
- `Annotation` - Render custom HTML children at a 3D world coordinate (supports dragging, lines, anchors)
- `Annotations` - Render multiple text-based overlays at 3D world coordinates (supports dragging, lines, anchors)

### Representation Components
- `GeometryRepresentation` - For surfaces, meshes, point clouds
- `Geometry2DRepresentation` - For 2D overlays
- `VolumeRepresentation` - For volume rendering
- `SliceRepresentation` - For 2D slices of 3D data


### Dataset Components
- `PolyData` - Polygonal geometry (points, lines, triangles)
- `ImageData` - Regular 3D grids (volumes)
- `Dataset` - Generic VTK dataset wrapper

### Data Array Components
- `DataArray` - Attach scalar/vector data
- `PointData` - Container for point-associated arrays
- `CellData` - Container for cell-associated arrays
- `FieldData` - Container for field data

### Algorithm & Reader Components
- `Algorithm` - VTK filters and sources
- `Reader` - File readers for OBJ, STL, VTK, etc.

### Interaction Components
- `Picking` - Mouse-based selection
- `VolumeController` - UI for volume transfer functions

### Data Sharing Components
- `ShareDataSetRoot` - Root for data sharing
- `RegisterDataSet` - Register shared data
- `UseDataSet` - Use registered data

## Manual Registration

If auto-discovery doesn't work, you can manually register the extension:

```python
from refast_vtk_js import VtkExtension

ui = RefastApp(
    title="VTK Demo",
    extensions=[VtkExtension()]
)
```

## Development

### Building the Frontend

```bash
cd frontend
npm install
npm run build
```

### Watch Mode

```bash
npm run dev
```

## License

MIT
