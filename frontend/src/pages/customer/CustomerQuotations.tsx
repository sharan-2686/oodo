import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Loader2, Calendar, Clock } from 'lucide-react';
import { quotationsApi } from '../../api/quotations';
import { Quotation } from '../../types';

const formatCurrency = (val: number | string): string => {
  const num = parseFloat(String(val));
  if (isNaN(num)) return '₹0';
  return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
};

const statusStyles: Record<string, string> = {
  draft: 'badge-muted',
  sent: 'badge-info',
  accepted: 'badge-success',
  rejected: 'badge-error',
  expired: 'badge-muted',
  converted: 'badge-purple',
};

const CustomerQuotations: React.FC = () => {
  const { data: quotations = [], isLoading } = useQuery<Quotation[]>({
    queryKey: ['customer-quotations'],
    queryFn: () => quotationsApi.list({ }),
    select: (data) => (Array.isArray(data) ? data : (data as any).items ?? []),
  });

  return (
    <div className="page-container animate-fade-in">
      <div className="section-header mb-6">
        <div className="flex items-center gap-2">
          <FileText size={20} style={{ color: '#6B1A2A' }} />
          <h1 className="section-title" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            My Quotes
          </h1>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={28} className="animate-spin" style={{ color: '#6B1A2A' }} />
        </div>
      ) : quotations.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <FileText size={40} className="mx-auto mb-3" style={{ color: '#E2D9D0' }} />
          <p className="text-ink font-medium mb-1">No quotations yet</p>
          <p className="text-sm text-muted">Your sales team will create quotes for you here.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {quotations.map((q) => {
            const statusClass = statusStyles[q.status] ?? 'badge-muted';
            return (
              <div key={q.id} className="glass-card p-5">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="font-semibold text-ink">{q.quote_number}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="flex items-center gap-1 text-xs text-muted">
                        <Calendar size={11} />
                        Issued: {new Date(q.issue_date).toLocaleDateString('en-IN')}
                      </span>
                      {q.valid_until && (
                        <span className="flex items-center gap-1 text-xs text-muted">
                          <Clock size={11} />
                          Valid until: {new Date(q.valid_until).toLocaleDateString('en-IN')}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`badge ${statusClass} capitalize`}>{q.status}</span>
                    <p className="text-lg font-bold text-ink mt-1"
                      style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
                      {formatCurrency(q.total_amount)}
                    </p>
                  </div>
                </div>

                {q.items && q.items.length > 0 && (
                  <div className="mt-3 pt-3" style={{ borderTop: '1px solid #E2D9D0' }}>
                    <div className="space-y-1.5">
                      {q.items.slice(0, 3).map((item) => (
                        <div key={item.id} className="flex justify-between text-xs text-muted">
                          <span>{item.description}</span>
                          <span className="font-medium text-ink">{formatCurrency(item.line_total)}</span>
                        </div>
                      ))}
                      {q.items.length > 3 && (
                        <p className="text-xs text-muted">+{q.items.length - 3} more items</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CustomerQuotations;
