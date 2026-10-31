import React from 'react';
import { cn } from '../../utils/cn';

export interface SelectOption {
  value: string | number;
  label: string;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  error?: string;
  helperText?: string;
}

export const Select = React.forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, options, error, helperText, id, ...props }, ref) => {
    const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={selectId} className="block text-xs font-semibold uppercase tracking-wider text-[#7A6860]">
            {label}
            {props.required && <span className="text-[#8B1A1A] ml-1">*</span>}
          </label>
        )}
        <select
          id={selectId}
          ref={ref}
          className={cn(
            'w-full bg-[#FAF7F2] border border-[#E2D9D0] rounded-lg px-3.5 py-2.5 text-sm text-[#1C1410] transition-all duration-200 cursor-pointer shadow-[inset_0_1px_3px_rgba(28,20,16,0.04)]',
            'focus:outline-none focus:border-[#6B1A2A] focus:ring-2 focus:ring-[#6B1A2A]/15',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            error && 'border-[#8B1A1A] focus:border-[#8B1A1A] focus:ring-[#8B1A1A]/15',
            className
          )}
          {...props}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} className="bg-[#FAF7F2] text-[#1C1410]">
              {opt.label}
            </option>
          ))}
        </select>
        {error && <p className="text-xs text-[#8B1A1A] mt-1">{error}</p>}
        {!error && helperText && <p className="text-xs text-[#7A6860] mt-1">{helperText}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';
