import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart2, TrendingUp, CreditCard, AlertTriangle, RefreshCw, Activity } from 'lucide-react';
import { dashboardApi } from '../../api/dashboard';
import { DashboardSummary } from '../../types';
import { useAuth } from '../../context/AuthContext';

const formatCurrency = (val: number | string): string => {
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) return '₹0';
  if (num >= 100000) return `₹${(num / 100000).toFixed(1)}L`;
  if (num >= 1000) return `₹${(num / 1000).toFixed(1)}K`;
  return `₹${num.toFixed(0)}`;
};

const StaffDashboard: React.FC = () => {
  const { user, hasPermission } = useAuth();
  const roleName = user?.role?.name?.toLowerCase() ?? '';
  const roleLabel = roleName.charAt(0).toUpperCase() + roleName.slice(1);

  const { data: summary, isLoading, isError, refetch } = useQuery<DashboardSummary>({
    queryKey: ['staff-dashboard'],
    queryFn: () => dashboardApi.getSummary(),
    enabled: hasPermission('dashboard:read'),
    refetchInterval: 120000,
  });

  return (
    <div className="page-container animate-fade-in">
      <div className="section-header mb-8">
        <div>
          <h1 className="text-2xl font-bold text-ink"
            style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            {roleLabel} Dashboard
          </h1>
          <p className="text-sm text-muted mt-0.5">
            Welcome back, {user?.full_name}. Here is your operational overview.
          </p>
        </div>
        {hasPermission('dashboard:read') && (
          <button onClick={() => refetch()} className="btn-secondary text-xs">
            <RefreshCw size={13} /> Refresh
          </button>
        )}
      </div>

      {!hasPermission('dashboard:read') ? (
        <div className="glass-card p-8 text-center">
          <p className="text-muted text-sm">Dashboard metrics are not available for your role.</p>
          <p className="text-muted text-xs mt-1">Use the sidebar to navigate to your permitted modules.</p>
        </div>
      ) : isLoading ? (
        <div className="grid grid-cols-2 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-card h-28 animate-pulse" style={{ background: '#F2EDE6' }} />
          ))}
        </div>
      ) : isError ? (
        <div className="glass-card p-8 text-center">
          <AlertTriangle size={28} className="mx-auto mb-3" style={{ color: '#C9A84C' }} />
          <p className="text-sm font-medium text-ink mb-1">Could not load dashboard data</p>
          <button onClick={() => refetch()} className="btn-primary text-xs mt-2">
            <RefreshCw size={12} /> Retry
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {hasPermission('subscription:read') && (
            <div className="glass-card p-6" style={{ borderLeft: '3px solid #6B1A2A' }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'rgba(107,26,42,0.1)' }}>
                  <Activity size={18} style={{ color: '#6B1A2A' }} />
                </div>
                <p className="text-xs font-semibold text-muted uppercase" style={{ letterSpacing: '0.06em' }}>
                  Active Subscriptions
                </p>
              </div>
              <p className="text-2xl font-bold text-ink" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
                {summary?.active_subscriptions_count ?? 0}
              </p>
            </div>
          )}

          {hasPermission('invoice:read') && (
            <div className="glass-card p-6" style={{ borderLeft: '3px solid #C9A84C' }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'rgba(201,168,76,0.1)' }}>
                  <TrendingUp size={18} style={{ color: '#C9A84C' }} />
                </div>
                <p className="text-xs font-semibold text-muted uppercase" style={{ letterSpacing: '0.06em' }}>
                  Revenue Collected
                </p>
              </div>
              <p className="text-2xl font-bold text-ink" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
                {formatCurrency(summary?.total_revenue_collected ?? 0)}
              </p>
            </div>
          )}

          {hasPermission('payments:read') && (
            <div className="glass-card p-6" style={{ borderLeft: '3px solid #B85C6E' }}>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: 'rgba(184,92,110,0.1)' }}>
                  <CreditCard size={18} style={{ color: '#B85C6E' }} />
                </div>
                <p className="text-xs font-semibold text-muted uppercase" style={{ letterSpacing: '0.06em' }}>
                  Revenue Owed
                </p>
              </div>
              <p className="text-2xl font-bold text-ink" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
                {formatCurrency(summary?.total_revenue_owed ?? 0)}
              </p>
            </div>
          )}

          {hasPermission('invoice:read') && (
            <div
              className="glass-card p-6"
              style={{ borderLeft: `3px solid ${summary?.overdue_invoices_count ? '#8B1A1A' : '#2D6A4F'}` }}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                  style={{ background: summary?.overdue_invoices_count ? 'rgba(139,26,26,0.1)' : 'rgba(45,106,79,0.1)' }}>
                  <AlertTriangle size={18} style={{ color: summary?.overdue_invoices_count ? '#8B1A1A' : '#2D6A4F' }} />
                </div>
                <p className="text-xs font-semibold text-muted uppercase" style={{ letterSpacing: '0.06em' }}>
                  Overdue Invoices
                </p>
              </div>
              <p className="text-2xl font-bold text-ink" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
                {summary?.overdue_invoices_count ?? 0}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Overdue invoices list for Finance */}
      {roleName === 'finance' && summary?.overdue_invoices && summary.overdue_invoices.length > 0 && (
        <div className="glass-card overflow-hidden mt-6">
          <div className="flex items-center gap-2 px-6 py-4" style={{ borderBottom: '1px solid #E2D9D0' }}>
            <AlertTriangle size={15} style={{ color: '#8B1A1A' }} />
            <h3 className="font-semibold text-ink text-sm">Overdue Invoices</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Customer</th>
                  <th>Due Date</th>
                  <th>Days Overdue</th>
                  <th>Balance</th>
                </tr>
              </thead>
              <tbody>
                {summary.overdue_invoices.slice(0, 8).map((inv) => (
                  <tr key={inv.id}>
                    <td className="font-medium" style={{ color: '#6B1A2A' }}>{inv.invoice_number}</td>
                    <td className="text-ink">{inv.customer_name}</td>
                    <td className="text-muted">{new Date(inv.due_date).toLocaleDateString('en-IN')}</td>
                    <td><span className="badge badge-error">{inv.days_overdue}d</span></td>
                    <td className="font-semibold text-ink">{formatCurrency(inv.balance_due)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default StaffDashboard;

