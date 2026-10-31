import React, { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { CreditCard, Loader2, AlertTriangle, CheckCircle, RefreshCw, Clock } from 'lucide-react';
import { invoicesApi } from '../../api/invoices';
import { Invoice } from '../../types';
import { openRazorpayCheckout, razorpayApi } from '../../api/razorpay';
import { useAuth } from '../../context/AuthContext';

const formatCurrency = (val: number | string): string => {
  const num = parseFloat(String(val));
  if (isNaN(num)) return '₹0';
  return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

const statusStyles: Record<string, { label: string; className: string }> = {
  draft: { label: 'Draft', className: 'badge-muted' },
  issued: { label: 'Issued', className: 'badge-info' },
  partially_paid: { label: 'Partially Paid', className: 'badge-warning' },
  paid: { label: 'Paid', className: 'badge-success' },
  overdue: { label: 'Overdue', className: 'badge-error' },
  void: { label: 'Void', className: 'badge-muted' },
  uncollectible: { label: 'Uncollectible', className: 'badge-error' },
};

const CustomerInvoices: React.FC = () => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [payingId, setPayingId] = useState<number | null>(null);
  const [paymentMsg, setPaymentMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const { data: invoices = [], isLoading } = useQuery<Invoice[]>({
    queryKey: ['customer-invoices'],
    queryFn: () => invoicesApi.list({}),
    select: (data) => (Array.isArray(data) ? data : (data as any).items ?? []),
  });

  const handlePay = async (invoice: Invoice) => {
    setPayingId(invoice.id);
    setPaymentMsg(null);
    try {
      const order = await razorpayApi.createOrder(invoice.id);
      await openRazorpayCheckout({
        keyId: order.razorpay_key_id,
        orderId: order.razorpay_order_id,
        amount: order.amount,
        currency: order.currency || 'INR',
        description: `Payment for Invoice ${order.invoice_number}`,
        customerName: order.customer_name || user?.full_name || '',
        customerEmail: order.customer_email || user?.email || '',
        onSuccess: async (response) => {
          try {
            await razorpayApi.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
              invoice_id: invoice.id,
            });
            setPaymentMsg({ type: 'success', text: `Payment for invoice ${invoice.invoice_number} was successful.` });
            queryClient.invalidateQueries({ queryKey: ['customer-invoices'] });
          } catch {
            setPaymentMsg({ type: 'error', text: 'Payment captured but verification failed. Please contact support.' });
          } finally {
            setPayingId(null);
          }
        },
        onError: (err) => {
          setPaymentMsg({ type: 'error', text: err?.error?.description || 'Payment failed. Please try again.' });
          setPayingId(null);
        },
        onDismiss: () => {
          setPayingId(null);
        },
      });
    } catch (err: any) {
      setPaymentMsg({ type: 'error', text: err?.message || 'Could not initiate payment. Please try again.' });
      setPayingId(null);
    }
  };

  const payableStatuses = ['issued', 'partially_paid', 'overdue'];

  return (
    <div className="page-container animate-fade-in">
      <div className="section-header mb-6">
        <div className="flex items-center gap-2">
          <CreditCard size={20} style={{ color: '#6B1A2A' }} />
          <h1 className="section-title" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            My Invoices
          </h1>
        </div>
        <button
          onClick={() => queryClient.invalidateQueries({ queryKey: ['customer-invoices'] })}
          className="btn-secondary text-xs"
        >
          <RefreshCw size={12} /> Refresh
        </button>
      </div>

      {paymentMsg && (
        <div
          className="flex items-center gap-2 px-4 py-3 rounded-lg mb-5 text-sm"
          style={
            paymentMsg.type === 'success'
              ? { background: '#D8F3DC', color: '#2D6A4F', border: '1px solid rgba(45,106,79,0.2)' }
              : { background: '#FFE5E5', color: '#8B1A1A', border: '1px solid rgba(139,26,26,0.2)' }
          }
        >
          {paymentMsg.type === 'success' ? <CheckCircle size={15} /> : <AlertTriangle size={15} />}
          {paymentMsg.text}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={28} className="animate-spin" style={{ color: '#6B1A2A' }} />
        </div>
      ) : invoices.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <CreditCard size={40} className="mx-auto mb-3" style={{ color: '#E2D9D0' }} />
          <p className="text-ink font-medium mb-1">No invoices yet</p>
          <p className="text-sm text-muted">Your invoices will appear here once generated.</p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Invoice</th>
                  <th>Issue Date</th>
                  <th>Due Date</th>
                  <th>Total</th>
                  <th>Balance Due</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => {
                  const status = statusStyles[inv.status] ?? { label: inv.status, className: 'badge-muted' };
                  const canPay = payableStatuses.includes(inv.status) && parseFloat(String(inv.balance_due)) > 0;
                  const isPaying = payingId === inv.id;
                  return (
                    <tr key={inv.id}>
                      <td>
                        <span className="font-medium" style={{ color: '#6B1A2A' }}>{inv.invoice_number}</span>
                      </td>
                      <td className="text-muted">{new Date(inv.issue_date).toLocaleDateString('en-IN')}</td>
                      <td className="text-muted">
                        <span className="flex items-center gap-1">
                          <Clock size={12} style={{ color: '#7A6860' }} />
                          {new Date(inv.due_date).toLocaleDateString('en-IN')}
                        </span>
                      </td>
                      <td className="font-medium text-ink">{formatCurrency(inv.total_amount)}</td>
                      <td className="font-semibold" style={{ color: canPay ? '#8B1A1A' : '#2D6A4F' }}>
                        {formatCurrency(inv.balance_due)}
                      </td>
                      <td>
                        <span className={`badge ${status.className}`}>{status.label}</span>
                      </td>
                      <td>
                        {canPay ? (
                          <button
                            onClick={() => handlePay(inv)}
                            disabled={isPaying || !!payingId}
                            className="btn-primary text-xs px-4 py-1.5"
                          >
                            {isPaying ? (
                              <><Loader2 size={12} className="animate-spin" /> Processing...</>
                            ) : (
                              <><CreditCard size={12} /> Pay Now</>
                            )}
                          </button>
                        ) : inv.status === 'paid' ? (
                          <span className="flex items-center gap-1 text-xs" style={{ color: '#2D6A4F' }}>
                            <CheckCircle size={12} /> Paid
                          </span>
                        ) : (
                          <span className="text-xs text-muted">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default CustomerInvoices;
