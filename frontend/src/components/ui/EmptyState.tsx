import React from 'react';
import { Button } from './Button';
import { Inbox } from 'lucide-react';

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-dashed border-[#E2D9D0] bg-[#F2EDE6]/40 backdrop-blur-sm my-6">
      <div className="w-14 h-14 rounded-2xl bg-[#F2EDE6] border border-[#E2D9D0] flex items-center justify-center text-[#6B1A2A] mb-4 shadow-glass-sm">
        {icon || <Inbox className="w-7 h-7" />}
      </div>
      <h3 className="text-base font-semibold text-[#1C1410] font-display">{title}</h3>
      <p className="text-xs text-[#7A6860] mt-1 max-w-sm leading-relaxed">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} size="sm" className="mt-5" variant="secondary">
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
