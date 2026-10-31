import React from 'react';
import { cn } from '../../utils/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'default' | 'cyan' | 'purple' | 'gold';
  dot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = 'default',
  dot = false,
  children,
  ...props
}) => {
  const variantStyles = {
    success: 'bg-[#D8F3DC] text-[#2D6A4F] border-[#B7E4C7]',
    warning: 'bg-[#FFF3CD] text-[#7B5E00] border-[#FFEAA7]',
    danger: 'bg-[#FFE5E5] text-[#8B1A1A] border-[#FFC9C9]',
    info: 'bg-[#E3F0FF] text-[#1A3A5C] border-[#BFDBFE]',
    cyan: 'bg-[#E3F0FF] text-[#1A3A5C] border-[#BFDBFE]',
    purple: 'bg-[#EDE9F8] text-[#4A2E8A] border-[#D6CDF4]',
    gold: 'bg-[#F9F5EB] text-[#8A6D1C] border-[#E8D48B]',
    default: 'bg-[#F2EDE6] text-[#7A6860] border-[#E2D9D0]',
  };

  const dotStyles = {
    success: 'bg-[#2D6A4F]',
    warning: 'bg-[#7B5E00]',
    danger: 'bg-[#8B1A1A]',
    info: 'bg-[#1A3A5C]',
    cyan: 'bg-[#1A3A5C]',
    purple: 'bg-[#4A2E8A]',
    gold: 'bg-[#C9A84C]',
    default: 'bg-[#7A6860]',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border tracking-wide uppercase',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {dot && <span className={cn('w-1.5 h-1.5 rounded-full', dotStyles[variant])} />}
      {children}
    </span>
  );
};
