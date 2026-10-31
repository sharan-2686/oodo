import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../api/dashboard';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatCurrency, formatDate } from '../utils/formatters';
import {
  TrendingUp,
  CreditCard,
  Users,
  AlertTriangle,
  ArrowUpRight,
  PlusCircle,
  FilePlus,
  Repeat,
  DollarSign,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const { data: summary, isLoading, error, refetch } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: () => dashboardApi.getSummary(),
    refetchInterval: 30000,
  });

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px]">
        <LoadingSpinner size="lg" />
        <p className="text-xs text-slate-400 mt-2 font-mono">CALCULATING REVENUE AGGREGATES...</p>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-rose-500/30 bg-rose-950/20 text-center p-8">
        <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
        <CardTitle className="text-rose-300">Failed to load dashboard metrics</CardTitle>
        <CardDescription className="text-slate-400 mt-1">
          Make sure the FastAPI backend server is running on port 8000.
        </CardDescription>
        <Button onClick={() => refetch()} variant="secondary" size="sm" className="mt-4">
          Retry Sync
        </Button>
      </Card>
    );
  }

  // Visual status chart data
  const statusData = Object.entries(summary?.subscriptions_by_status || {}).map(
    ([status, count]) => ({
      status: status.toUpperCase(),
      count: count,
    })
  );

  // Revenue trajectory mock/derived series for Recharts
  const revenueChartData = [
    { period: 'May', collected: Number(summary?.total_revenue_collected || 0) * 0.45, owed: 5000 },
    { period: 'Jun', collected: Number(summary?.total_revenue_collected || 0) * 0.60, owed: 7500 },
    { period: 'Jul', collected: Number(summary?.total_revenue_collected || 0) * 0.72, owed: 6200 },
    { period: 'Aug', collected: Number(summary?.total_revenue_collected || 0) * 0.85, owed: 8900 },
    { period: 'Sep', collected: Number(summary?.total_revenue_collected || 0) * 0.92, owed: 6400 },
    { period: 'Current', collected: Number(summary?.total_revenue_collected || 0), owed: Number(summary?.total_revenue_owed || 0) },
  ];

  return (
    <div className="space-y-8">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-2 border-b border-white/5">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Revenue Operations Hub
            <Badge variant="cyan" className="text-[10px] ml-2">Live Sync</Badge>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time subscription billing health, invoice receivables, and receivables ledger.
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Button
            size="sm"
            variant="secondary"
            leftIcon={<PlusCircle className="w-3.5 h-3.5 text-cyan-400" />}
            onClick={() => navigate('/customers')}
          >
            New Customer
          </Button>
          <Button
            size="sm"
            variant="secondary"
            leftIcon={<FilePlus className="w-3.5 h-3.5 text-indigo-400" />}
            onClick={() => navigate('/quotations')}
          >
            Draft Quote
          </Button>
          <Button
            size="sm"
            variant="primary"
            leftIcon={<CreditCard className="w-3.5 h-3.5 text-slate-950" />}
            onClick={() => navigate('/payments')}
          >
            Record Payment
          </Button>
        </div>
      </div>

      {/* KPI Stat Cards (4 Cards Grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Card 1: Total Revenue Collected */}
        <Card interactive className="border-white/10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Collected Revenue
            </span>
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <DollarSign className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono tabular-nums text-white mt-3">
            {formatCurrency(summary?.total_revenue_collected)}
          </div>
          <p className="text-[11px] text-emerald-400 font-medium mt-1.5 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" /> Fully settled allocations
          </p>
        </Card>

        {/* Card 2: Revenue Owed / Unpaid */}
        <Card interactive className="border-white/10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Outstanding Balance
            </span>
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono tabular-nums text-amber-300 mt-3">
            {formatCurrency(summary?.total_revenue_owed)}
          </div>
          <p className="text-[11px] text-slate-400 font-medium mt-1.5">
            Across {summary?.total_invoices_count || 0} total invoices
          </p>
        </Card>

        {/* Card 3: Active Subscriptions */}
        <Card interactive className="border-white/10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Active Subscriptions
            </span>
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Repeat className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono tabular-nums text-white mt-3">
            {summary?.active_subscriptions_count || 0}
          </div>
          <p className="text-[11px] text-cyan-400 font-medium mt-1.5">
            Recurring active billing engines
          </p>
        </Card>

        {/* Card 4: Overdue Invoices Alert */}
        <Card interactive className="border-white/10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Overdue Receivables
            </span>
            <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-mono tabular-nums text-rose-400 mt-3">
            {summary?.overdue_invoices_count || 0}
          </div>
          <p className="text-[11px] text-rose-400 font-medium mt-1.5">
            Require dunning & follow-up
          </p>
        </Card>
      </div>

      {/* Main Charts & Breakdown Section (2-Column) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Revenue Trajectory Area Chart */}
        <Card className="lg:col-span-2 border-white/10">
          <CardHeader className="flex flex-row items-center justify-between mb-2">
            <div>
              <CardTitle>Cash Flow & Revenue Velocity</CardTitle>
              <CardDescription>
                Historical collected proceeds vs outstanding accounts receivable.
              </CardDescription>
            </div>
            <Badge variant="cyan">INR ₹</Badge>
          </CardHeader>
          <CardContent>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={revenueChartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCollected" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#00f0ff" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="colorOwed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="period" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} tickFormatter={(val) => `₹${val / 1000}k`} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 23, 42, 0.95)',
                      borderColor: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                    }}
                    formatter={(val: any) => formatCurrency(val)}
                  />
                  <Area
                    type="monotone"
                    dataKey="collected"
                    name="Collected"
                    stroke="#00f0ff"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorCollected)"
                  />
                  <Area
                    type="monotone"
                    dataKey="owed"
                    name="Owed"
                    stroke="#f43f5e"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorOwed)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Right 1 Col: Subscription Status Breakdown */}
        <Card className="border-white/10 flex flex-col justify-between">
          <CardHeader>
            <CardTitle>Subscriptions by Status</CardTitle>
            <CardDescription>Active, trialing, paused, and cancelled fleet.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {statusData.length > 0 ? (
              <div className="h-44 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={statusData}>
                    <XAxis dataKey="status" stroke="#64748b" fontSize={9} tickLine={false} />
                    <YAxis stroke="#64748b" fontSize={10} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderRadius: '0.75rem',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p className="text-xs text-slate-500 text-center py-8">No subscriptions registered yet.</p>
            )}

            <div className="pt-3 border-t border-white/5 space-y-2">
              {Object.entries(summary?.subscriptions_by_status || {}).map(([st, cnt]) => (
                <div key={st} className="flex items-center justify-between text-xs">
                  <span className="text-slate-400 capitalize">{st.replace('_', ' ')}</span>
                  <span className="font-mono font-bold text-slate-200">{cnt}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Overdue Invoices Alert Table */}
      {summary?.overdue_invoices && summary.overdue_invoices.length > 0 && (
        <Card className="border-rose-500/20 bg-rose-950/10">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-rose-300 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                Critical Overdue Invoices Requiring Action
              </CardTitle>
              <CardDescription>
                Outstanding invoices that have exceeded their contractual payment due dates.
              </CardDescription>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => navigate('/invoices')}
              rightIcon={<ArrowUpRight className="w-3.5 h-3.5" />}
            >
              Open Invoices Ledger
            </Button>
          </CardHeader>

          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400 uppercase tracking-wider font-semibold">
                    <th className="py-2.5 px-3">Invoice #</th>
                    <th className="py-2.5 px-3">Customer</th>
                    <th className="py-2.5 px-3">Due Date</th>
                    <th className="py-2.5 px-3">Days Past Due</th>
                    <th className="py-2.5 px-3 text-right">Balance Due</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {summary.overdue_invoices.map((inv) => (
                    <tr key={inv.id} className="hover:bg-white/5">
                      <td className="py-3 px-3 font-mono font-semibold text-cyan-300">
                        {inv.invoice_number}
                      </td>
                      <td className="py-3 px-3 text-slate-200 font-medium">{inv.customer_name}</td>
                      <td className="py-3 px-3 text-slate-400">{formatDate(inv.due_date)}</td>
                      <td className="py-3 px-3">
                        <Badge variant="danger" className="text-[10px]">
                          {inv.days_overdue} days
                        </Badge>
                      </td>
                      <td className="py-3 px-3 text-right font-mono font-bold text-rose-400">
                        {formatCurrency(inv.balance_due)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

