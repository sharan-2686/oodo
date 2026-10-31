import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import {
  TrendingUp, Users, AlertTriangle, CreditCard,
  RefreshCw, DollarSign, Activity,
} from 'lucide-react';
import { dashboardApi } from '../../api/dashboard';
import { DashboardSummary } from '../../types';

const COLORS = ['#6B1A2A', '#C9A84C', '#B85C6E', '#8B2535', '#E8D48B'];

// Mock revenue trend data (replace with real API when available)
const mockRevenueTrend = [
  { month: 'Jun', revenue: 42000, collected: 38000 },
  { month: 'Jul', revenue: 55000, collected: 49000 },
  { month: 'Aug', revenue: 48000, collected: 44000 },
  { month: 'Sep', revenue: 62000, collected: 58000 },
  { month: 'Oct', revenue: 71000, collected: 65000 },
  { month: 'Nov', revenue: 58000, collected: 53000 },
];

const formatCurrency = (val: number | string): string => {
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) return '₹0';
  if (num >= 100000) return `₹${(num / 100000).toFixed(1)}L`;
  if (num >= 1000) return `₹${(num / 1000).toFixed(1)}K`;
  return `₹${num.toFixed(0)}`;
};

interface StatCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: React.ElementType;
  accent?: string;
  badge?: string;
  badgeType?: 'success' | 'warning' | 'error';
}

const StatCard: React.FC<StatCardProps> = ({ title, value, subtitle, icon: Icon, accent = '#6B1A2A', badge, badgeType = 'info' }) => {
  const badgeColors = {
    success: { bg: '#D8F3DC', color: '#2D6A4F' },
    warning: { bg: '#FFF3CD', color: '#7B5E00' },
    error: { bg: '#FFE5E5', color: '#8B1A1A' },
    info: { bg: '#E3F0FF', color: '#1A3A5C' },
  };
  const bc = badgeColors[badgeType];

  return (
    <div
      className="glass-card stat-card p-6"
      style={{ borderLeft: `3px solid ${accent}` }}
    >
      <div className="flex items-start justify-between mb-4">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center"
          style={{ background: `${accent}15` }}
        >
          <Icon size={20} style={{ color: accent }} />
        </div>
        {badge && (
          <span
            className="text-xs font-medium px-2 py-0.5 rounded-full"
            style={{ background: bc.bg, color: bc.color }}
          >
            {badge}
          </span>
        )}
      </div>
      <p className="text-xs font-semibold text-muted uppercase tracking-wider mb-1"
        style={{ letterSpacing: '0.06em' }}>
        {title}
      </p>
      <p className="text-2xl font-bold text-ink mb-1"
        style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
        {value}
      </p>
      {subtitle && <p className="text-xs text-muted">{subtitle}</p>}
    </div>
  );
};

const AdminDashboard: React.FC = () => {
  const { data: summary, isLoading, isError, refetch } = useQuery<DashboardSummary>({
    queryKey: ['admin-dashboard'],
    queryFn: () => dashboardApi.getSummary(),
    refetchInterval: 60000,
  });

  const subscriptionPieData = summary
    ? Object.entries(summary.subscriptions_by_status).map(([name, value]) => ({ name, value }))
    : [];

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="glass-card p-6 h-32 animate-pulse" style={{ background: '#F2EDE6' }} />
          ))}
        </div>
        <div className="glass-card p-6 h-72 animate-pulse" style={{ background: '#F2EDE6' }} />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="page-container">
        <div className="glass-card p-8 text-center">
          <AlertTriangle size={32} className="mx-auto mb-3" style={{ color: '#C9A84C' }} />
          <p className="text-ink font-medium mb-1">Dashboard data unavailable</p>
          <p className="text-sm text-muted mb-4">Could not connect to the API. Ensure the backend is running.</p>
          <button onClick={() => refetch()} className="btn-primary">
            <RefreshCw size={14} /> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container animate-fade-in">
      {/* Page header */}
      <div className="section-header mb-8">
        <div>
          <h1 className="text-2xl font-bold text-ink"
            style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            Administration Dashboard
          </h1>
          <p className="text-sm text-muted mt-0.5">Real-time overview of your revenue operations</p>
        </div>
        <button onClick={() => refetch()} className="btn-secondary text-xs">
          <RefreshCw size={13} /> Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Active Subscriptions"
          value={String(summary?.active_subscriptions_count ?? 0)}
          subtitle="Currently billing"
          icon={Activity}
          accent="#6B1A2A"
          badge="Live"
          badgeType="success"
        />
        <StatCard
          title="Revenue Collected"
          value={formatCurrency(summary?.total_revenue_collected ?? 0)}
          subtitle="Total payments received"
          icon={TrendingUp}
          accent="#C9A84C"
        />
        <StatCard
          title="Revenue Owed"
          value={formatCurrency(summary?.total_revenue_owed ?? 0)}
          subtitle="Outstanding balance"
          icon={DollarSign}
          accent="#B85C6E"
        />
        <StatCard
          title="Overdue Invoices"
          value={String(summary?.overdue_invoices_count ?? 0)}
          subtitle={`of ${summary?.total_invoices_count ?? 0} total invoices`}
          icon={AlertTriangle}
          accent={summary?.overdue_invoices_count ? '#8B1A1A' : '#2D6A4F'}
          badge={summary?.overdue_invoices_count ? 'Action Required' : 'All Clear'}
          badgeType={summary?.overdue_invoices_count ? 'error' : 'success'}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Revenue Trend — 2/3 width */}
        <div className="glass-card p-6 lg:col-span-2">
          <h3 className="font-semibold text-ink mb-1 text-sm">Revenue Trend</h3>
          <p className="text-xs text-muted mb-5">Billed vs Collected over last 6 months</p>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={mockRevenueTrend} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6B1A2A" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#6B1A2A" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#C9A84C" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#C9A84C" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2D9D0" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#7A6860' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#7A6860' }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v / 1000}K`} />
              <Tooltip
                contentStyle={{ background: '#FAF7F2', border: '1px solid #E2D9D0', borderRadius: '8px', fontSize: '12px' }}
                formatter={(val: number) => [`₹${val.toLocaleString()}`, '']}
              />
              <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              <Area type="monotone" dataKey="revenue" name="Billed" stroke="#6B1A2A" strokeWidth={2} fill="url(#revGrad)" dot={false} />
              <Area type="monotone" dataKey="collected" name="Collected" stroke="#C9A84C" strokeWidth={2} fill="url(#colGrad)" dot={false} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Subscription Pie — 1/3 width */}
        <div className="glass-card p-6">
          <h3 className="font-semibold text-ink mb-1 text-sm">Subscriptions by Status</h3>
          <p className="text-xs text-muted mb-5">Current distribution</p>
          {subscriptionPieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={subscriptionPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {subscriptionPieData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#FAF7F2', border: '1px solid #E2D9D0', borderRadius: '8px', fontSize: '12px' }}
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48">
              <p className="text-sm text-muted">No subscription data</p>
            </div>
          )}
        </div>
      </div>

      {/* Subscription Bar Chart */}
      <div className="glass-card p-6 mb-8">
        <h3 className="font-semibold text-ink mb-1 text-sm">Subscription Volume</h3>
        <p className="text-xs text-muted mb-5">Count of subscriptions per status</p>
        {subscriptionPieData.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={subscriptionPieData} margin={{ left: -20, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2D9D0" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#7A6860' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#7A6860' }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: '#FAF7F2', border: '1px solid #E2D9D0', borderRadius: '8px', fontSize: '12px' }}
              />
              <Bar dataKey="value" name="Count" radius={[4, 4, 0, 0]}>
                {subscriptionPieData.map((_entry, index) => (
                  <Cell key={`bar-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="text-center py-8 text-muted text-sm">No data available</div>
        )}
      </div>

      {/* Overdue Invoices Table */}
      {summary?.overdue_invoices && summary.overdue_invoices.length > 0 && (
        <div className="glass-card overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid #E2D9D0' }}>
            <div className="flex items-center gap-2">
              <AlertTriangle size={16} style={{ color: '#8B1A1A' }} />
              <h3 className="font-semibold text-ink text-sm">Overdue Invoices Requiring Attention</h3>
            </div>
            <span className="badge badge-error">{summary.overdue_invoices.length} overdue</span>
          </div>
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Customer</th>
                  <th>Due Date</th>
                  <th>Days Overdue</th>
                  <th>Balance Due</th>
                </tr>
              </thead>
              <tbody>
                {summary.overdue_invoices.slice(0, 10).map((inv) => (
                  <tr key={inv.id}>
                    <td>
                      <span className="font-medium text-primary">{inv.invoice_number}</span>
                    </td>
                    <td className="text-ink">{inv.customer_name}</td>
                    <td className="text-muted">{new Date(inv.due_date).toLocaleDateString('en-IN')}</td>
                    <td>
                      <span className="badge badge-error">{inv.days_overdue}d overdue</span>
                    </td>
                    <td className="font-semibold text-ink">{formatCurrency(inv.balance_due)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quick Links */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-8">
        {[
          { label: 'Manage Customers', path: '/admin/customers', icon: Users, color: '#6B1A2A' },
          { label: 'View Quotations', path: '/admin/quotations', icon: CreditCard, color: '#C9A84C' },
          { label: 'Check Invoices', path: '/admin/invoices', icon: CreditCard, color: '#B85C6E' },
          { label: 'Track Payments', path: '/admin/payments', icon: TrendingUp, color: '#8B2535' },
        ].map((link) => (
          <a
            key={link.path}
            href={link.path}
            className="glass-card p-4 flex items-center gap-3 hover:shadow-glass-md transition-all duration-200 group"
            style={{ textDecoration: 'none' }}
          >
            <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ background: `${link.color}15` }}>
              <link.icon size={16} style={{ color: link.color }} />
            </div>
            <span className="text-sm font-medium text-ink group-hover:text-primary transition-colors">
              {link.label}
            </span>
          </a>
        ))}
      </div>
    </div>
  );
};

export default AdminDashboard;

