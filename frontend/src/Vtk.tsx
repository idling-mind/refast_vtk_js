/**
 * Vtk React Component
 *
 * This is the React implementation of the Vtk component.
 * It receives props from the Python component via WebSocket and renders the UI.
 */

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { cn } from './utils';

export interface VtkProps {
  /** Component ID - used for targeting with ctx.bound_js() */
  id?: string;
  /** CSS classes to apply */
  className?: string;
  /** The current value */
  value?: string;
  /** Callback when value changes */
  onChange?: (value: string) => void;
  /** Additional inline styles */
  style?: React.CSSProperties;
  /** Refast internal ID for tracking */
  'data-refast-id'?: string;
}

/**
 * Vtk component
 * 
 * Refast extension for vtk
 */
export function Vtk({
  id,
  className,
  value: initialValue = '',
  onChange,
  style,
  'data-refast-id': dataRefastId,
}: VtkProps): React.ReactElement {
  const wrapperRef = useRef<HTMLDivElement>(null);
  const [value, setValue] = useState(initialValue);

  // Update internal state when prop changes
  useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  // Handle value change
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setValue(newValue);
    onChange?.(newValue);
  }, [onChange]);

  // Expose methods on the DOM element for ctx.bound_js() and ctx.call_bound_js()
  useEffect(() => {
    const wrapper = wrapperRef.current;
    if (!wrapper) return;

    // Attach methods to the DOM element so they can be called via document.getElementById()
    (wrapper as any).getValue = () => value;
    (wrapper as any).setValue = (newValue: string) => {
      setValue(newValue);
      onChange?.(newValue);
    };
    (wrapper as any).reset = () => {
      setValue(initialValue);
      onChange?.(initialValue);
    };

    // Cleanup: remove methods when component unmounts
    return () => {
      delete (wrapper as any).getValue;
      delete (wrapper as any).setValue;
      delete (wrapper as any).reset;
    };
  }, [value, initialValue, onChange]);

  return (
    <div
      ref={wrapperRef}
      id={id}
      className={cn(
        'refast_vtk_js',
        'inline-flex flex-col gap-2',
        className
      )}
      data-refast-id={dataRefastId}
      style={style}
    >
      {/* 
        Replace this with your actual component implementation.
        This is a simple example showing:
        - Input handling with onChange callback
        - Exposed methods for ctx.bound_js()
        - Proper Tailwind styling
      */}
      <label className="text-sm font-medium text-foreground">
        Vtk
      </label>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        className={cn(
          'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2',
          'text-sm ring-offset-background',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50'
        )}
        placeholder="Enter a value..."
      />
      <p className="text-xs text-muted-foreground">
        Current value: {value || '(empty)'}
      </p>
    </div>
  );
}

Vtk.displayName = 'Vtk';
