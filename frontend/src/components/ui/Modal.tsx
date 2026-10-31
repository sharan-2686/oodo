import React, { useEffect } from 'react';
import { cn } from '../../utils/cn';
import { X } from 'lucide-react';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '4xl';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = 'lg',
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '4xl': 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-[#1C1410]/50 backdrop-blur-sm transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Glass Dialog */}
      <div
        className={cn(
          'relative w-full rounded-2xl border border-[#E2D9D0] bg-[#FAF7F2] p-6 shadow-glass-lg z-10 my-8 transition-all duration-300 scale-100',
          maxWidthClasses[maxWidth]
        )}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-[#7A6860] hover:text-[#1C1410] p-1.5 rounded-lg hover:bg-[#F2EDE6] transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="mb-4 pr-8">
          <h2 className="text-xl font-bold text-[#1C1410] tracking-tight font-display">{title}</h2>
          {description && <p className="text-xs text-[#7A6860] mt-1">{description}</p>}
        </div>

        {/* Content Body */}
        <div className="max-h-[75vh] overflow-y-auto pr-1 text-[#1C1410]">{children}</div>

        {/* Optional Footer */}
        {footer && (
          <div className="mt-6 pt-4 border-t border-[#E2D9D0] flex items-center justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};
