import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'gold' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const isBusy = loading || isLoading;

  const baseClass = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
    gold: 'btn-gold',
    outline: 'btn-secondary',
    ghost: 'btn-secondary',
  }[variant];

  const sizeStyle = {
    sm: { padding: '6px 12px', fontSize: '0.75rem' },
    md: { padding: '10px 20px', fontSize: '0.875rem' },
    lg: { padding: '12px 28px', fontSize: '1rem' },
  }[size];

  return (
    <button
      className={`${baseClass} ${className}`}
      style={{
        ...sizeStyle,
        opacity: disabled || isBusy ? 0.6 : 1,
        cursor: disabled || isBusy ? 'not-allowed' : 'pointer',
      }}
      disabled={disabled || isBusy}
      {...props}
    >
      {isBusy ? (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Loading...
        </span>
      ) : (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          {leftIcon}
          {children}
          {rightIcon}
        </span>
      )}
    </button>
  );
};
export default Button;
