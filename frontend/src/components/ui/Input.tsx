import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className = '', ...props }, ref) => {
    return (
      <div>
        {label && <label className="form-label">{label}</label>}
        <input
          ref={ref}
          className={`form-input ${error ? 'border-red-400' : ''} ${className}`}
          style={error ? { borderColor: '#8B1A1A', boxShadow: '0 0 0 3px rgba(139,26,26,0.10)' } : undefined}
          {...props}
        />
        {error && <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{error}</p>}
        {hint && !error && <p className="text-xs text-muted mt-1">{hint}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
