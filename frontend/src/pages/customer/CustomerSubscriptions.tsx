import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Loader2, Calendar, Activity } from 'lucide-react';
import { subscriptionsApi } from '../../api/subscriptions';
import { Subscription } from '../../types';

const formatCurrency = (val: number | string): string => {
  const num = parseFloat(String(val));
  if (isNaN(num)) return '₹0';
  return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
};

const statusStyles: Record<string, { label: string; className: string }> = {
  draft: { label: 'Draft', className: 'badge-muted' },
  trialing: { label: 'Trial', className: 'badge-info' },
  active: { label: 'Active', className: 'badge-success' },
  past_due: { label: 'Past Due', className: 'badge-warning' },
  paused: { label: 'Paused', className: 'badge-muted' },
  cancelled: { label: 'Cancelled', className: 'badge-error' },
  expired: { label: 'Expired', className: 'badge-muted' },
};

const CustomerSubscriptions: React.FC = () => {
  const { data: subscriptions = [], isLoading } = useQuery<Subscription[]>({
    queryKey: ['customer-subscriptions'],
    queryFn: () => subscriptionsApi.list({ }),
    select: (data) => (Array.isArray(data) ? data : (data as any).items ?? []),
  });

  return (
    <div className="page-container animate-fade-in">
      <div className="section-header mb-6">
        <div className="flex items-center gap-2">
          <Activity size={20} style={{ color: '#6B1A2A' }} />
          <h1 className="section-title" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            My Subscriptions
          </h1>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={28} className="animate-spin" style={{ color: '#6B1A2A' }} />
        </div>
      ) : subscriptions.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Activity size={40} className="mx-auto mb-3" style={{ color: '#E2D9D0' }} />
          <p className="text-ink font-medium mb-1">No subscriptions yet</p>
          <p className="text-sm text-muted">Your active subscriptions will appear here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {subscriptions.map((sub) => {
            const s = statusStyles[sub.status] ?? { label: sub.status, className: 'badge-muted' };
            return (
              <div key={sub.id} className="glass-card p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-ink">{sub.subscription_number}</p>
                      <span className={`badge ${s.className}`}>{s.label}</span>
                    </div>
                    <p className="text-xs text-muted mt-0.5">
                      Billing: {sub.interval_count}x {sub.billing_interval}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-ink"
                      style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
                      {formatCurrency(sub.unit_price)}
                    </p>
                    <p className="text-xs text-muted">per {sub.billing_interval}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-3 pt-3"
                  style={{ borderTop: '1px solid #E2D9D0' }}>
                  {sub.start_date && (
                    <div>
                      <p className="text-xs text-muted mb-0.5">Start Date</p>
                      <p className="text-xs font-medium text-ink flex items-center gap-1">
                        <Calendar size={11} style={{ color: '#6B1A2A' }} />
                        {new Date(sub.start_date).toLocaleDateString('en-IN')}
                      </p>
                    </div>
                  )}
                  {sub.next_billing_at && (
                    <div>
                      <p className="text-xs text-muted mb-0.5">Next Billing</p>
                      <p className="text-xs font-medium text-ink flex items-center gap-1">
                        <Calendar size={11} style={{ color: '#C9A84C' }} />
                        {new Date(sub.next_billing_at).toLocaleDateString('en-IN')}
                      </p>
                    </div>
                  )}
                  {sub.trial_ends_at && (
                    <div>
                      <p className="text-xs text-muted mb-0.5">Trial Ends</p>
                      <p className="text-xs font-medium text-ink">
                        {new Date(sub.trial_ends_at).toLocaleDateString('en-IN')}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CustomerSubscriptions;
