import React from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { Shield, Activity } from 'lucide-react';
import { Badge } from '../ui/Badge';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { user } = useAuth();

  const getPageTitle = (path: string): string => {
    if (path.startsWith('/dashboard')) return 'Executive Revenue Dashboard';
    if (path.startsWith('/customers')) return 'Customer Directory & Accounts';
    if (path.startsWith('/products')) return 'Product & Variant Catalog';
    if (path.startsWith('/plans')) return 'Subscription Plans & Tiers';
    if (path.startsWith('/quotations')) return 'Sales Quotations & Proposals';
    if (path.startsWith('/subscriptions')) return 'Subscription Lifecycle Operations';
    if (path.startsWith('/invoices')) return 'Invoicing & Receivables';
    if (path.startsWith('/payments')) return 'Payment Transactions & Allocations';
    return 'Brightloop 360';
  };

  return (
    <header className="h-16 sticky top-0 z-20 glass-nav px-8 flex items-center justify-between">
      {/* Title Breadcrumb */}
      <div className="flex items-center gap-3">
        <h1 className="text-base font-bold text-white tracking-tight">{getPageTitle(location.pathname)}</h1>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* API Health indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900/80 border border-white/10 text-xs">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span className="text-slate-300 text-xs">Production Engine Online</span>
        </div>

        {/* Role status pill */}
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-cyan-400" />
          <span className="text-xs text-slate-300 font-mono">
            {user?.role?.name} Mode
          </span>
          <Badge variant="cyan" className="text-[10px]">
            {user?.permissions?.length || 0} PERMS
          </Badge>
        </div>
      </div>
    </header>
  );
};

