import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { paymentsApi } from '../api/payments';
import { customersApi } from '../api/customers';
import { invoicesApi } from '../api/invoices';
import { PaymentCreateInput } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatCurrency, formatDateTime, getStatusBadgeVariant } from '../utils/formatters';
import { Plus, CreditCard, Split } from 'lucide-react';

export const PaymentsPage: React.FC = () => {
  const queryClient = useQueryClient();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [customerId, setCustomerId] = useState<number | undefined>(undefined);
  const [amount, setAmount] = useState<number>(15000);
  const [paymentMethod, setPaymentMethod] = useState<PaymentCreateInput['payment_method']>('bank_transfer');
  const [transactionRef, setTransactionRef] = useState(`UTR-${Date.now().toString().slice(-8)}`);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState<number | undefined>(undefined);
  const [formError, setFormError] = useState<string | null>(null);

  // Queries
  const { data: payments, isLoading } = useQuery({
    queryKey: ['payments'],
    queryFn: () => paymentsApi.list(),
  });

  const { data: customerList } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.list({ limit: 100 }),
  });

  const { data: unpaidInvoices } = useQuery({
    queryKey: ['unpaid-invoices', customerId],
    queryFn: () => invoicesApi.list({ customer_id: customerId }),
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: PaymentCreateInput) => paymentsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      setIsModalOpen(false);
      resetForm();
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to record payment');
    },
  });

  const resetForm = () => {
    setCustomerId(undefined);
    setAmount(15000);
    setTransactionRef(`UTR-${Date.now().toString().slice(-8)}`);
    setSelectedInvoiceId(undefined);
    setFormError(null);
  };

  const handleRecordPayment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setFormError('Please select a customer');
      return;
    }
    if (amount <= 0) {
      setFormError('Payment amount must be greater than zero');
      return;
    }

    const payload: PaymentCreateInput = {
      customer_id: Number(customerId),
      amount: Number(amount),
      currency: 'INR',
      payment_method: paymentMethod,
      transaction_reference: transactionRef,
      allocations: selectedInvoiceId
        ? [{ invoice_id: Number(selectedInvoiceId), amount: Number(amount) }]
        : undefined,
    };

    createMutation.mutate(payload);
  };

  const customerInvoices = (unpaidInvoices || []).filter(
    (inv) => !customerId || inv.customer_id === Number(customerId)
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[#1C1410] font-display flex items-center gap-2">
            Payment Transactions & Ledger
          </h2>
          <p className="text-xs text-[#7A6860] mt-1">
            Capture received settlement funds across UPI, Net Banking, and Gateways, and allocate them across outstanding invoices.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            if (customerList?.items?.length) setCustomerId(customerList.items[0].id);
            setIsModalOpen(true);
          }}
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Record Incoming Payment
        </Button>
      </div>

      {/* Payments Table */}
      {isLoading ? (
        <LoadingSpinner />
      ) : !payments || payments.length === 0 ? (
        <EmptyState
          title="No payments captured"
          description="Record incoming payments from clients and reconcile them against open invoices."
          actionLabel="Record Payment"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Payment #</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Payment Method</TableHead>
              <TableHead>Transaction Ref / UTR</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Allocated Balance</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Recorded At</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {payments.map((p) => {
              const statusBadge = getStatusBadgeVariant(p.status);
              const customerObj = customerList?.items?.find((c) => c.id === p.customer_id);

              return (
                <TableRow key={p.id}>
                  <TableCell className="font-mono font-semibold text-[#6B1A2A]">
                    {p.payment_number}
                  </TableCell>
                  <TableCell>
                    <div className="font-semibold text-[#1C1410]">
                      {customerObj?.name || `Customer #${p.customer_id}`}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className="inline-flex items-center gap-1.5 text-xs text-[#1C1410] uppercase font-mono">
                      <CreditCard className="w-3.5 h-3.5 text-[#6B1A2A]" />
                      {p.payment_method.replace('_', ' ')}
                    </span>
                  </TableCell>
                  <TableCell className="font-mono text-xs text-[#7A6860]">
                    {p.transaction_reference || 'N/A'}
                  </TableCell>
                  <TableCell className="font-mono text-sm font-bold text-[#2D6A4F]">
                    {formatCurrency(p.amount)}
                  </TableCell>
                  <TableCell>
                    <div className="text-xs font-mono text-[#1C1410]">
                      <span>Allocated: {formatCurrency(p.total_allocated)}</span>
                      {Number(p.unallocated_amount) > 0 && (
                        <div className="text-[#7B5E00] text-[10px]">
                          Unallocated: {formatCurrency(p.unallocated_amount)}
                        </div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusBadge.variant} dot>
                      {statusBadge.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-xs text-[#7A6860]">
                    {formatDateTime(p.created_at)}
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* Record Payment Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Record Payment & Allocate"
        description="Capture payment confirmation and reconcile immediately against open invoices."
      >
        <form onSubmit={handleRecordPayment} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <Select
            label="Payer Customer"
            value={customerId || ''}
            onChange={(e) => setCustomerId(Number(e.target.value))}
            options={(customerList?.items || []).map((c) => ({
              value: c.id,
              label: `${c.name} (${c.customer_code})`,
            }))}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Received Amount (INR)"
              type="number"
              min="1"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
              required
            />
            <Select
              label="Payment Channel"
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value as any)}
              options={[
                { value: 'upi', label: 'UPI / VPA Transfer' },
                { value: 'bank_transfer', label: 'NEFT / RTGS / IMPS' },
                { value: 'card', label: 'Credit / Debit Card' },
                { value: 'gateway', label: 'Online Payment Gateway' },
                { value: 'cash', label: 'Cash Settlement' },
              ]}
            />
          </div>

          <Input
            label="Transaction Ref / Bank UTR Number"
            placeholder="e.g. UTR-982348723948"
            value={transactionRef}
            onChange={(e) => setTransactionRef(e.target.value)}
          />

          {/* Allocation Selector */}
          <div className="p-3.5 rounded-xl bg-[#F2EDE6] border border-[#E2D9D0] space-y-2">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-[#1C1410]">
              <Split className="w-3.5 h-3.5 text-[#6B1A2A]" />
              <span>Direct Invoice Allocation (Optional)</span>
            </div>
            <p className="text-[11px] text-[#7A6860] leading-relaxed">
              Allocate this received amount directly to settle an outstanding customer invoice.
            </p>
            <Select
              value={selectedInvoiceId || ''}
              onChange={(e) => setSelectedInvoiceId(e.target.value ? Number(e.target.value) : undefined)}
              options={[
                { value: '', label: 'Leave as Unallocated Credit' },
                ...customerInvoices.map((inv) => ({
                  value: inv.id,
                  label: `${inv.invoice_number} — Due: ${formatCurrency(inv.balance_due)}`,
                })),
              ]}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Record & Allocate
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
