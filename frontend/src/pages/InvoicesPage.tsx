import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { invoicesApi } from '../api/invoices';
import { customersApi } from '../api/customers';
import { Invoice, InvoiceCreateOneTimeInput } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatCurrency, formatDate, getStatusBadgeVariant } from '../utils/formatters';
import { Plus, Eye, CheckCircle, Ban, Printer, Trash2 } from 'lucide-react';

export const InvoicesPage: React.FC = () => {
  const queryClient = useQueryClient();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedInvoiceForView, setSelectedInvoiceForView] = useState<Invoice | null>(null);

  // Queries
  const { data: invoices, isLoading } = useQuery({
    queryKey: ['invoices'],
    queryFn: () => invoicesApi.list(),
  });

  const { data: customerList } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.list({ limit: 100 }),
  });

  // Create One-Time Form State
  const [customerId, setCustomerId] = useState<number | undefined>(undefined);
  const [notes, setNotes] = useState('Payment terms: Net 15 days from invoice issuance.');
  const [items, setItems] = useState<Array<{
    description_snapshot: string;
    quantity: number;
    unit_price: number;
    tax_rate_percent: number;
  }>>([
    { description_snapshot: 'Professional Services / Setup Fee', quantity: 1, unit_price: 15000, tax_rate_percent: 18 },
  ]);
  const [formError, setFormError] = useState<string | null>(null);

  React.useEffect(() => {
    if (!customerId && customerList?.items?.length) {
      setCustomerId(customerList.items[0].id);
    }
  }, [customerList, customerId]);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: InvoiceCreateOneTimeInput) => invoicesApi.createOneTime(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      setIsCreateModalOpen(false);
      resetCreateForm();
    },
    onError: (err: any) => {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ')
        : 'Failed to create invoice';
      setFormError(msg);
    },
  });

  const actionMutation = useMutation({
    mutationFn: ({ id, action }: { id: number; action: string }) =>
      invoicesApi.executeAction(id, action),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
    },
    onError: (err: any) => {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ')
        : 'Action failed';
      alert(msg);
    },
  });

  const resetCreateForm = () => {
    setCustomerId(customerList?.items?.[0]?.id);
    setNotes('Payment terms: Net 15 days from invoice issuance.');
    setItems([
      { description_snapshot: 'Professional Services / Setup Fee', quantity: 1, unit_price: 15000, tax_rate_percent: 18 },
    ]);
    setFormError(null);
  };

  const handleAddItem = () => {
    setItems([
      ...items,
      { description_snapshot: 'Additional Service / Deliverable', quantity: 1, unit_price: 5000, tax_rate_percent: 18 },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length <= 1) return;
    setItems(items.filter((_, i) => i !== index));
  };

  const handleCreateInvoice = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setFormError('Please select a customer');
      return;
    }
    createMutation.mutate({
      customer_id: Number(customerId),
      notes,
      items,
    });
  };

  const handlePrint = () => {
    window.print();
  };

  // Live Calculations for Modal
  const calculatedSubtotal = items.reduce((acc, it) => acc + (it.quantity * it.unit_price), 0);
  const calculatedTax = items.reduce((acc, it) => acc + (it.quantity * it.unit_price * (it.tax_rate_percent / 100)), 0);
  const calculatedTotal = calculatedSubtotal + calculatedTax;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[#1C1410] font-display flex items-center gap-2">
            Invoicing & Accounts Receivable
          </h2>
          <p className="text-xs text-[#7A6860] mt-1">
            Automated recurring subscription bills, one-time manual invoices, and payment reconciliation tracking.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            resetCreateForm();
            setIsCreateModalOpen(true);
          }}
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Create One-Time Invoice
        </Button>
      </div>

      {/* Invoices Table */}
      {isLoading ? (
        <LoadingSpinner />
      ) : !invoices || invoices.length === 0 ? (
        <EmptyState
          title="No invoices generated"
          description="Invoices are created automatically when subscriptions bill, or you can draft a one-time invoice."
          actionLabel="Create Invoice"
          onAction={() => {
            resetCreateForm();
            setIsCreateModalOpen(true);
          }}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Invoice #</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Issue / Due Date</TableHead>
              <TableHead>Total Amount</TableHead>
              <TableHead>Paid</TableHead>
              <TableHead>Balance Due</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {invoices.map((inv) => {
              const statusBadge = getStatusBadgeVariant(inv.status);

              return (
                <TableRow key={inv.id}>
                  <TableCell className="font-mono font-semibold text-[#6B1A2A]">
                    {inv.invoice_number}
                  </TableCell>
                  <TableCell>
                    <div className="font-semibold text-[#1C1410]">{inv.customer_name_snapshot}</div>
                    {inv.customer_email_snapshot && (
                      <div className="text-xs text-[#7A6860]">{inv.customer_email_snapshot}</div>
                    )}
                  </TableCell>
                  <TableCell className="text-xs text-[#7A6860]">
                    <div>Issued: {formatDate(inv.issue_date)}</div>
                    <div>Due: {formatDate(inv.due_date)}</div>
                  </TableCell>
                  <TableCell className="font-mono text-xs font-semibold text-[#1C1410]">
                    {formatCurrency(inv.total_amount)}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-[#2D6A4F] font-semibold">
                    {formatCurrency(inv.amount_paid)}
                  </TableCell>
                  <TableCell className="font-mono text-sm font-bold text-[#8B1A1A]">
                    {formatCurrency(inv.balance_due)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusBadge.variant} dot>
                      {statusBadge.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {/* View Printable Invoice */}
                      <Button
                        size="sm"
                        variant="secondary"
                        title="View Document"
                        onClick={() => setSelectedInvoiceForView(inv)}
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </Button>

                      {/* Confirm Draft */}
                      {inv.status === 'draft' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => actionMutation.mutate({ id: inv.id, action: 'confirm' })}
                        >
                          <CheckCircle className="w-3 h-3 mr-1 text-[#2D6A4F]" />
                          Confirm
                        </Button>
                      )}

                      {/* Void Invoice */}
                      {inv.status !== 'void' && inv.status !== 'paid' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          title="Void Invoice"
                          onClick={() => actionMutation.mutate({ id: inv.id, action: 'void' })}
                          className="text-[#8B1A1A] border-[#FFC9C9]"
                        >
                          <Ban className="w-3.5 h-3.5" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* Invoice Document Preview Modal (Print Ready) */}
      {selectedInvoiceForView && (
        <Modal
          isOpen={!!selectedInvoiceForView}
          onClose={() => setSelectedInvoiceForView(null)}
          title={`Tax Invoice ${selectedInvoiceForView.invoice_number}`}
          description={`Issued to ${selectedInvoiceForView.customer_name_snapshot}`}
          maxWidth="4xl"
          footer={
            <Button
              variant="primary"
              onClick={handlePrint}
            >
              <Printer className="w-4 h-4 mr-1.5" />
              Print / Save PDF
            </Button>
          }
        >
          <div className="p-8 rounded-2xl bg-[#FAF7F2] border border-[#E2D9D0] space-y-8 text-[#1C1410] shadow-glass-sm">
            {/* Header */}
            <div className="flex justify-between items-start border-b border-[#E2D9D0] pb-6">
              <div>
                <h1 className="text-2xl font-extrabold text-[#6B1A2A] font-display tracking-tight">BRIGHTLOOP 360</h1>
                <p className="text-xs text-[#7A6860] mt-1">Enterprise Cloud Subscription Platform</p>
                <p className="text-xs text-[#7A6860]">GSTIN: 29ABCDE1234F1Z5</p>
              </div>
              <div className="text-right">
                <span className="text-xs uppercase text-[#7A6860] font-semibold tracking-wider">TAX INVOICE</span>
                <p className="text-xl font-mono font-bold text-[#6B1A2A] mt-1">
                  {selectedInvoiceForView.invoice_number}
                </p>
                <p className="text-xs text-[#7A6860] mt-1">
                  Issue Date: {formatDate(selectedInvoiceForView.issue_date)}
                </p>
                <p className="text-xs text-[#7A6860]">
                  Due Date: {formatDate(selectedInvoiceForView.due_date)}
                </p>
              </div>
            </div>

            {/* Billed To */}
            <div className="grid grid-cols-2 gap-6 text-xs">
              <div>
                <span className="text-[#7A6860] uppercase font-semibold">Billed To:</span>
                <p className="text-sm font-bold text-[#1C1410] mt-1">
                  {selectedInvoiceForView.customer_name_snapshot}
                </p>
                {selectedInvoiceForView.customer_email_snapshot && (
                  <p className="text-[#7A6860] mt-0.5">{selectedInvoiceForView.customer_email_snapshot}</p>
                )}
              </div>
              <div className="text-right">
                <span className="text-[#7A6860] uppercase font-semibold">Payment Status:</span>
                <div className="mt-1">
                  <Badge variant={getStatusBadgeVariant(selectedInvoiceForView.status).variant}>
                    {selectedInvoiceForView.status.toUpperCase()}
                  </Badge>
                </div>
              </div>
            </div>

            {/* Line Items Table */}
            <div className="border border-[#E2D9D0] rounded-xl overflow-hidden bg-[#F2EDE6]">
              <table className="w-full text-left text-xs">
                <thead className="border-b border-[#E2D9D0] bg-[#E2D9D0]/50">
                  <tr className="text-[#7A6860] uppercase font-semibold">
                    <th className="p-3">Description</th>
                    <th className="p-3 text-right">Qty</th>
                    <th className="p-3 text-right">Unit Price</th>
                    <th className="p-3 text-right">Tax (GST)</th>
                    <th className="p-3 text-right">Total</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2D9D0]">
                  {(selectedInvoiceForView.items || []).map((it) => (
                    <tr key={it.id}>
                      <td className="p-3 font-medium text-[#1C1410]">{it.description_snapshot}</td>
                      <td className="p-3 text-right font-mono text-[#1C1410]">{it.quantity}</td>
                      <td className="p-3 text-right font-mono text-[#1C1410]">{formatCurrency(it.unit_price)}</td>
                      <td className="p-3 text-right font-mono text-[#7A6860]">{formatCurrency(it.line_tax)}</td>
                      <td className="p-3 text-right font-mono font-semibold text-[#1C1410]">
                        {formatCurrency(it.line_total)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Financial Summary Totals */}
            <div className="flex justify-end text-xs">
              <div className="w-72 space-y-2">
                <div className="flex justify-between text-[#7A6860]">
                  <span>Subtotal:</span>
                  <span className="font-mono text-[#1C1410]">
                    {formatCurrency(selectedInvoiceForView.subtotal)}
                  </span>
                </div>
                <div className="flex justify-between text-[#7A6860]">
                  <span>Taxes (GST):</span>
                  <span className="font-mono text-[#1C1410]">
                    {formatCurrency(selectedInvoiceForView.tax_amount)}
                  </span>
                </div>
                <div className="flex justify-between text-sm font-bold text-[#1C1410] pt-2 border-t border-[#E2D9D0]">
                  <span>Total Amount:</span>
                  <span className="font-mono text-[#6B1A2A]">
                    {formatCurrency(selectedInvoiceForView.total_amount)}
                  </span>
                </div>
                <div className="flex justify-between text-[#2D6A4F] font-semibold">
                  <span>Amount Paid:</span>
                  <span className="font-mono">
                    {formatCurrency(selectedInvoiceForView.amount_paid)}
                  </span>
                </div>
                <div className="flex justify-between text-[#8B1A1A] font-bold border-t border-[#E2D9D0] pt-1.5">
                  <span>Outstanding Balance Due:</span>
                  <span className="font-mono">
                    {formatCurrency(selectedInvoiceForView.balance_due)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </Modal>
      )}

      {/* Create One-Time Invoice Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Issue One-Time Invoice"
        description="Bill a customer directly outside of regular recurring subscriptions."
      >
        <form onSubmit={handleCreateInvoice} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <Select
            label="Customer Account"
            value={customerId || ''}
            onChange={(e) => setCustomerId(Number(e.target.value))}
            options={[
              { value: '', label: '-- Select Customer Account --' },
              ...(customerList?.items || []).map((c) => ({
                value: c.id,
                label: `${c.name} (${c.customer_code})`,
              })),
            ]}
            required
          />

          {/* Dynamic Line Items */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#1C1410] uppercase tracking-wider">
                Invoice Line Items
              </span>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={handleAddItem}
              >
                <Plus className="w-3.5 h-3.5 mr-1" />
                Add Row
              </Button>
            </div>

            <div className="space-y-2.5">
              {items.map((item, idx) => (
                <div
                  key={idx}
                  className="grid grid-cols-12 gap-2 p-3 rounded-xl bg-[#F2EDE6] border border-[#E2D9D0] items-center"
                >
                  <div className="col-span-5">
                    <Input
                      placeholder="Description / Deliverable"
                      value={item.description_snapshot}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].description_snapshot = e.target.value;
                        setItems(updated);
                      }}
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      min="1"
                      placeholder="Qty"
                      value={item.quantity}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].quantity = Number(e.target.value) || 1;
                        setItems(updated);
                      }}
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      min="0"
                      step="0.01"
                      placeholder="Price"
                      value={item.unit_price}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].unit_price = parseFloat(e.target.value) || 0;
                        setItems(updated);
                      }}
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="GST %"
                      value={item.tax_rate_percent}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].tax_rate_percent = parseFloat(e.target.value) || 0;
                        setItems(updated);
                      }}
                    />
                  </div>
                  <div className="col-span-1 flex justify-center">
                    {items.length > 1 && (
                      <button
                        type="button"
                        onClick={() => handleRemoveItem(idx)}
                        className="text-[#8B1A1A] hover:bg-[#FFE5E5] p-1.5 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Live Summary */}
          <div className="p-3.5 rounded-xl bg-[#FAF7F2] border border-[#E2D9D0] space-y-1.5 text-xs">
            <div className="flex justify-between text-[#7A6860]">
              <span>Subtotal:</span>
              <span className="font-mono text-[#1C1410] font-semibold">{formatCurrency(calculatedSubtotal)}</span>
            </div>
            <div className="flex justify-between text-[#7A6860]">
              <span>Estimated Tax (GST):</span>
              <span className="font-mono text-[#1C1410] font-semibold">{formatCurrency(calculatedTax)}</span>
            </div>
            <div className="flex justify-between text-sm font-bold text-[#1C1410] pt-1.5 border-t border-[#E2D9D0]">
              <span>Invoice Total:</span>
              <span className="font-mono text-[#6B1A2A]">{formatCurrency(calculatedTotal)}</span>
            </div>
          </div>

          <Input
            label="Invoice Notes & Payment Terms"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Issue Invoice
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
