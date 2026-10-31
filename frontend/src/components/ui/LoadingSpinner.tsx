import React from 'react';
import { cn } from '../../utils/cn';

export const LoadingSpinner: React.FC<{ className?: string; size?: 'sm' | 'md' | 'lg' }> = ({
  className,
  size = 'md',
}) => {
  const sizeMap = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={cn('flex items-center justify-center p-8', className)}>
      <div className="relative">
        <div
          className={cn(
            'rounded-full border-2 border-[#E2D9D0] border-t-[#6B1A2A] animate-spin',
            sizeMap[size]
          )}
        />
        <div
          className={cn(
            'absolute inset-0 rounded-full blur-sm bg-[#6B1A2A]/10 animate-pulse pointer-events-none',
            sizeMap[size]
          )}
        />
      </div>
    </div>
  );
};
