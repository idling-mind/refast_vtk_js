# vtk-js - AI Agent Instructions

> **Purpose**: This file provides instructions for AI coding agents (GitHub Copilot, Cursor, etc.) working on this Refast extension.

## Project Overview

**vtk-js** is a Refast extension that provides custom React components accessible from Python. This extension follows the Refast extension architecture pattern.

### Key Concepts

1. **Python Components** define the API and serialize to JSON
2. **React Components** render the UI in the browser
3. **Extension Class** registers components and manages static assets
4. **Auto-discovery** via Python entry points

---

## Project Structure

```
refast_vtk_js/
├── pyproject.toml                    # Package configuration with entry point
├── hatch_build.py                    # Build hook for frontend compilation
├── README.md
├── AGENTS.md                         # THIS FILE - AI agent instructions
├── src/
│   └── refast_vtk_js/
│       ├── __init__.py               # Extension class + exports
│       ├── components.py             # Python component definitions
│       ├── py.typed                  # Type hints marker
│       └── static/                   # Built frontend assets (generated)
│           ├── refast_vtk_js.js
│           └── refast_vtk_js.css
├── frontend/                         # React source code
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
│       └── index.tsx                 # React components + registration
└── tests/
    └── test_components.py
```

---

## Creating Python Components

### Location
All Python components go in `src/refast_vtk_js/components.py`

### Template

```python
from typing import Any, Literal
from refast.components.base import Component


class MyComponent(Component):
    """
    Brief description of the component.
    
    Example:
        ```python
        from refast_vtk_js import MyComponent
        
        MyComponent(
            title="Hello",
            value=42,
            on_click=ctx.callback(handle_click)
        )
        ```
    
    Args:
        title: The title to display
        value: Numeric value
        on_click: Optional click callback
        id: Component ID (required for ctx.bound_js() calls)
        class_name: CSS classes
    """
    
    component_type: str = "MyComponent"  # MUST match React component name
    
    def __init__(
        self,
        title: str,
        value: int = 0,
        on_click: Any = None,
        id: str | None = None,
        class_name: str = "",
        **props: Any,
    ):
        super().__init__(id=id, class_name=class_name, **props)
        self.title = title
        self.value = value
        self.on_click = on_click
    
    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {
                "title": self.title,
                "value": self.value,
                "on_click": self.on_click.serialize() if self.on_click else None,
                "class_name": self.class_name,
                **self._serialize_extra_props(),
            },
            "children": self._render_children(),
        }
```

### Critical Rules for Python Components

1. **Use `snake_case` for all prop names** in `render()` - the frontend auto-converts to camelCase
2. **`component_type` MUST match** the React component name exactly
3. **Serialize callbacks** using `.serialize()` method
4. **Include `id` prop** if component has bound methods callable via `ctx.bound_js()`
5. **Export from `__init__.py`** for user convenience

### Registering Components

Add to `src/refast_vtk_js/__init__.py`:

```python
from .components import MyComponent

class VtkExtension(Extension):
    # ...
    
    @property
    def components(self) -> list:
        return [MyComponent]  # Add your component here

__all__ = ["VtkExtension", "MyComponent"]  # Export it
```

---

## Creating React Components

### Location
All React components go in `frontend/src/index.tsx`

### Template

```tsx
import React from 'react';

// Get Refast client utilities
const { componentRegistry, React: R } = window.RefastClient;

interface MyComponentProps {
  title: string;
  value?: number;
  onClick?: (data: Record<string, unknown>) => void;  // Already a function!
  className?: string;
  children?: React.ReactNode;
  'data-refast-id'?: string;
}

const MyComponent: React.FC<MyComponentProps> = ({
  title,
  value = 0,
  onClick,
  className,
  children,
  'data-refast-id': dataRefastId,
}) => {
  const handleClick = () => {
    // onClick is already a function - ComponentRenderer converted it
    if (onClick) {
      onClick({ value, title });  // Data becomes ctx.event_data in Python
    }
  };
  
  return (
    <div
      id={dataRefastId}
      className={className}
      onClick={handleClick}
    >
      <h3>{title}</h3>
      <span>{value}</span>
      {children}
    </div>
  );
};

// CRITICAL: Register with the EXACT name used in Python's component_type
componentRegistry.register('MyComponent', MyComponent);
```

### Critical Rules for React Components

1. **Use camelCase for prop names** - ComponentRenderer converts snake_case from Python
2. **Callbacks are already functions** - Just call them with event data
3. **Register name MUST match** Python's `component_type` exactly
4. **Include `data-refast-id`** prop and set it as the element's `id` for bound method support
5. **Use Tailwind CSS** for styling, not inline styles
6. **Don't bundle React** - Use `window.RefastClient.React` 

### Handling Different Callback Scenarios

#### Standard Callbacks (Most Cases)
```tsx
// ComponentRenderer converts callback refs to functions
const MyComponent: React.FC<Props> = ({ onClick }) => {
  const handleClick = () => {
    onClick?.({ value: 42 });  // Just call it!
  };
  return <button onClick={handleClick}>Click</button>;
};
```

#### Library-Managed Events (ECharts, D3, Canvas, etc.)
When wrapping libraries that manage their own event systems:

```tsx
// Type for raw callback references (not processed by ComponentRenderer)
interface CallbackRef {
  callbackId: string;
  boundArgs?: Record<string, unknown>;
}

// Helper to manually invoke callbacks
function invokeCallback(callback: CallbackRef | undefined, data: Record<string, unknown> = {}): void {
  if (!callback?.callbackId) return;
  
  const event = new CustomEvent('refast:callback', {
    detail: {
      callbackId: callback.callbackId,
      data: { ...(callback.boundArgs || {}), ...data },
    },
  });
  window.dispatchEvent(event);
}

// Usage with library events
useEffect(() => {
  chart.on('click', (params) => {
    invokeCallback(onClick, { x: params.x, y: params.y });
  });
}, [onClick]);
```

### Exposing Component Methods

For components with imperative APIs (canvas, video, etc.):

```tsx
import React, { forwardRef, useRef, useEffect } from 'react';

export interface MyCanvasRef {
  clear: () => void;
  undo: () => void;
  getData: () => unknown;
}

interface MyCanvasProps {
  id?: string;
  'data-refast-id'?: string;
}

const MyCanvas = forwardRef<MyCanvasRef | null, MyCanvasProps>(
  ({ id, 'data-refast-id': dataRefastId }, ref) => {
    const internalRef = useRef<HTMLCanvasElement>(null);
    
    // Expose methods on the DOM element for ctx.bound_js() / ctx.call_bound_js()
    useEffect(() => {
      const element = document.getElementById(id || dataRefastId || '');
      if (!element) return;
      
      (element as any).clear = () => {
        // Clear canvas logic
      };
      
      (element as any).undo = () => {
        // Undo logic
      };
      
      (element as any).getData = () => {
        // Return data
      };
      
      return () => {
        // Cleanup
        delete (element as any).clear;
        delete (element as any).undo;
        delete (element as any).getData;
      };
    }, [id, dataRefastId]);
    
    return <canvas ref={internalRef} id={id || dataRefastId} />;
  }
);

componentRegistry.register('MyCanvas', MyCanvas);
```

---

## Build Process

### Development

```bash
# Install frontend dependencies
cd frontend && npm install

# Build frontend (outputs to src/refast_vtk_js/static/)
npm run build

# Watch mode for development
npm run dev
```

### Installation

```bash
# Install package locally (hatch_build.py auto-builds frontend)
pip install -e .

# Or build distribution
pip install build
python -m build
```

### Vite Configuration

The `frontend/vite.config.ts` is pre-configured to:
- Output UMD bundle to `../src/refast_vtk_js/static/`
- Externalize React (uses Refast's bundled version)
- Generate separate CSS file

---

## Testing

### Python Tests

```python
# tests/test_components.py
import pytest
from refast_vtk_js import MyComponent


class MockCallback:
    """Mock callback for testing."""
    def serialize(self):
        return {"callbackId": "test-callback-id"}


class TestMyComponent:
    def test_render_basic(self):
        comp = MyComponent(title="Test", value=42)
        result = comp.render()
        
        assert result["type"] == "MyComponent"
        assert result["props"]["title"] == "Test"
        assert result["props"]["value"] == 42
    
    def test_render_with_callback(self):
        callback = MockCallback()
        comp = MyComponent(title="Test", on_click=callback)
        result = comp.render()
        
        assert result["props"]["on_click"] == {"callbackId": "test-callback-id"}
    
    def test_render_with_children(self):
        comp = MyComponent(title="Parent")
        comp.add_child("Child text")
        result = comp.render()
        
        assert result["children"] == ["Child text"]
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/refast_vtk_js

# Run specific test
pytest tests/test_components.py::TestMyComponent::test_render_basic -v
```

---

## Common Patterns

### Component with Children

```python
# Python
class Container(Component):
    component_type = "Container"
    
    def __init__(self, gap: str = "md", **kwargs):
        super().__init__(**kwargs)
        self.gap = gap
    
    def render(self) -> dict[str, Any]:
        return {
            "type": self.component_type,
            "id": self.id,
            "props": {"gap": self.gap, "class_name": self.class_name},
            "children": self._render_children(),
        }

# Usage
Container(
    gap="lg"
    children=[
      MyComponent(title="First"),
      MyComponent(title="Second"),
    ]
)
```

```tsx
// React
const Container: React.FC<ContainerProps> = ({ gap = 'md', className, children }) => {
  const gapClasses = { sm: 'gap-2', md: 'gap-4', lg: 'gap-6' };
  return (
    <div className={`flex flex-col ${gapClasses[gap]} ${className || ''}`}>
      {children}
    </div>
  );
};
```

### Component with Validation

```python
from typing import Literal

class StatusBadge(Component):
    component_type = "StatusBadge"
    
    def __init__(
        self,
        status: Literal["success", "warning", "error", "info"],
        label: str,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if status not in ("success", "warning", "error", "info"):
            raise ValueError(f"Invalid status: {status}")
        self.status = status
        self.label = label
```

### Wrapping External React Libraries

```tsx
// Import the library
import { ExternalWidget } from 'some-react-library';

// Wrap it for Refast
const WrappedWidget: React.FC<WidgetProps> = (props) => {
  // Transform props if needed
  const { onClick, onHover, ...rest } = props;
  
  return (
    <ExternalWidget
      {...rest}
      onItemClick={(item) => onClick?.({ item })}
      onItemHover={(item) => onHover?.({ item })}
    />
  );
};

componentRegistry.register('ExternalWidget', WrappedWidget);
```

---

## Debugging

### Browser Console Commands

```javascript
// List all registered components
window.RefastClient.componentRegistry.list()

// Check if component is registered
window.RefastClient.componentRegistry.has('MyComponent')

// Get component
window.RefastClient.componentRegistry.get('MyComponent')

// Check Refast version
window.RefastClient.version
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Component not rendering | Check `component_type` matches registration name |
| Callbacks not firing | Ensure `.serialize()` is called in Python `render()` |
| Props undefined in React | Check snake_case → camelCase conversion |
| Static files 404 | Verify `static_path` in extension class |
| React errors | Ensure not bundling React (use external) |

---

## Best Practices Summary

### Python Side
- ✅ Use `snake_case` for all prop names
- ✅ Include comprehensive docstrings with examples
- ✅ Use type hints everywhere
- ✅ Serialize callbacks with `.serialize()`
- ✅ Export components from `__init__.py`

### React Side
- ✅ Use TypeScript with strict types
- ✅ Use Tailwind CSS for styling
- ✅ Include `data-refast-id` prop
- ✅ Don't bundle React
- ✅ Guard component registration with `has()` check

### General
- ✅ Match `component_type` exactly between Python and React
- ✅ Test both Python serialization and React rendering
- ✅ Document bound methods in docstrings
- ✅ Keep static assets in `static/` directory

---

## Quick Reference

### Callback Flow
```
Python ctx.callback(fn) → serialize() → JSON → WebSocket → 
ComponentRenderer → JavaScript function → onClick(data) → 
WebSocket → Python fn(ctx) with ctx.event_data
```

### Prop Transformation
```
Python: {"on_click": ..., "max_value": 10, "class_name": "..."}
   ↓ ComponentRenderer
React: {onClick: fn, maxValue: 10, className: "..."}
```

### Extension Loading Order
1. `refast-client.css` loads
2. Extension CSS files load
3. `refast-client.js` loads → exposes `window.RefastClient`
4. Extension JS files load → register components

---

## Resources

- [Refast Documentation](https://github.com/idling-mind/refast)
- [Component Development Guide](https://github.com/idling-mind/refast/blob/main/docs/COMPONENT_DEVELOPMENT.md)
- [Extension Development Guide](https://github.com/idling-mind/refast/blob/main/docs/EXTENSION_DEVELOPMENT.md)
