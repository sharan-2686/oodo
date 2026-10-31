import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { quotationsApi } from '../api/quotations';
import { customersApi } from '../api/customers';
import { catalogApi } from '../api/catalog';
import { Quotation, QuotationCreateInput, QuotationConvertRequest } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatCurrency, formatDate, getStatusBadgeVariant } from '../utils/formatters';
import { Plus, Trash2, Send, CheckCircle, ArrowRightCircle, Check } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const QuotationsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isConvertModalOpen, setIsConvertModalOpen] = useState(false);
  const [selectedQuoteForConvert, setSelectedQuoteForConvert] = useState<Quotation | null>(null);

  // Queries
  const { data: quotations, isLoading } = useQuery({
    queryKey: ['quotations'],
    queryFn: () => quotationsApi.list(),
  });

  const { data: customerList } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.list({ limit: 100 }),
  });

  const { data: plans } = useQuery({
    queryKey: ['plans'],
    queryFn: () => catalogApi.listPlans(),
  });

  // Create Form State
  const [customerId, setCustomerId] = useState<number | undefined>(undefined);
  const [currency, setCurrency] = useState('INR');
  const [terms, setTerms] = useState('Payment due within 15 days upon acceptance.');
  const [items, setItems] = useState<Array<{
    description: string;
    quantity: number;
    unit_price: number;
    tax_rate_percent: number;
  }>>([
    { description: 'Cloud Platform Subscription (Standard)', quantity: 1, unit_price: 4999, tax_rate_percent: 18 },
  ]);
  const [formError, setFormError] = useState<string | null>(null);

  // Convert Form State
  const [convertPlanId, setConvertPlanId] = useState<number | undefined>(undefined);
  const [convertBillingInterval, setConvertBillingInterval] = useState<'month' | 'year' | 'week' | 'day'>('month');

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: QuotationCreateInput) => quotationsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      setIsCreateModalOpen(false);
      resetCreateForm();
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to create quotation');
    },
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      quotationsApi.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
    },
  });

  const convertMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: QuotationConvertRequest }) =>
      quotationsApi.convertToSubscription(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['quotations'] });
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
      setIsConvertModalOpen(false);
      navigate('/staff/subscriptions');
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to convert quotation');
    },
  });

  const resetCreateForm = () => {
    setCustomerId(undefined);
    setItems([{ description: 'Cloud Platform Subscription (Standard)', quantity: 1, unit_price: 4999, tax_rate_percent: 18 }]);
    setFormError(null);
  };

  const handleAddItem = () => {
    setItems([
      ...items,
      { description: 'Additional Service / Add-on', quantity: 1, unit_price: 999, tax_rate_percent: 18 },
    ]);
  };

  const handleRemoveItem = (index: number) => {
    if (items.length <= 1) return;
    setItems(items.filter((_, i) => i !== index));
  };

  const handleCreateQuotation = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerId) {
      setFormError('Please select a customer');
      return;
    }
    createMutation.mutate({
      customer_id: Number(customerId),
      currency,
      terms,
      items,
    });
  };

  const openConvertModal = (quote: Quotation) => {
    setSelectedQuoteForConvert(quote);
    if (plans && plans.length > 0) {
      setConvertPlanId(plans[0].id);
    }
    setIsConvertModalOpen(true);
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
            Sales Quotations & Proposals
          </h2>
          <p className="text-xs text-[#7A6860] mt-1">
            Build itemized recurring quotes, calculate taxes, and convert accepted quotes into live subscriptions.
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
          Create New Quotation
        </Button>
      </div>

      {/* Quotations Table */}
      {isLoading ? (
        <LoadingSpinner />
      ) : !quotations || quotations.length === 0 ? (
        <EmptyState
          title="No quotations drafted"
          description="Draft sales proposals with line items and discounts to send to customers."
          actionLabel="Create Quotation"
          onAction={() => {
            resetCreateForm();
            setIsCreateModalOpen(true);
          }}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Quote Number</TableHead>
              <TableHead>Client & Entity</TableHead>
              <TableHead>Date Issued</TableHead>
              <TableHead>Subtotal</TableHead>
              <TableHead>Taxes</TableHead>
              <TableHead>Total Amount</TableHead>
              <TableHead>Workflow Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {quotations.map((q) => {
              const statusBadge = getStatusBadgeVariant(q.status);
              const customerObj = customerList?.items?.find((c) => c.id === q.customer_id);

              return (
                <TableRow key={q.id}>
                  <TableCell className="font-mono font-semibold text-[#6B1A2A]">
                    {q.quote_number}
                  </TableCell>
                  <TableCell>
                    <div className="font-semibold text-[#1C1410]">
                      {customerObj?.name || `Customer #${q.customer_id}`}
                    </div>
                    {customerObj?.company_name && (
                      <div className="text-xs text-[#7A6860]">{customerObj.company_name}</div>
                    )}
                  </TableCell>
                  <TableCell className="text-[#7A6860] text-xs">{formatDate(q.issue_date)}</TableCell>
                  <TableCell className="font-mono text-xs text-[#1C1410]">
                    {formatCurrency(q.subtotal)}
                  </TableCell>
                  <TableCell className="font-mono text-xs text-[#7A6860]">
                    {formatCurrency(q.tax_amount)}
                  </TableCell>
                  <TableCell className="font-mono text-sm font-bold text-[#1C1410]">
                    {formatCurrency(q.total_amount)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusBadge.variant} dot>
                      {statusBadge.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {/* Draft -> Send */}
                      {q.status === 'draft' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => statusMutation.mutate({ id: q.id, status: 'sent' })}
                        >
                          <Send className="w-3 h-3 mr-1 text-[#6B1A2A]" />
                          Send
                        </Button>
                      )}

                      {/* Sent -> Accept / Reject */}
                      {q.status === 'sent' && (
                        <>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => statusMutation.mutate({ id: q.id, status: 'accepted' })}
                          >
                            <CheckCircle className="w-3 h-3 mr-1 text-[#2D6A4F]" />
                            Accept
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => statusMutation.mutate({ id: q.id, status: 'rejected' })}
                            className="text-[#8B1A1A] border-[#FFC9C9]"
                          >
                            Reject
                          </Button>
                        </>
                      )}

                      {/* Accepted -> Convert to Subscription */}
                      {q.status === 'accepted' && (
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => openConvertModal(q)}
                        >
                          <ArrowRightCircle className="w-3.5 h-3.5 mr-1" />
                          Convert
                        </Button>
                      )}

                      {/* Converted badge */}
                      {q.status === 'converted' && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-mono text-[#2D6A4F] font-medium">
                          <Check className="w-3.5 h-3.5" />
                          Subscription Active
                        </span>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* Convert to Subscription Modal */}
      {isConvertModalOpen && selectedQuoteForConvert && (
        <Modal
          isOpen={isConvertModalOpen}
          onClose={() => setIsConvertModalOpen(false)}
          title={`Convert Quote ${selectedQuoteForConvert.quote_number} to Subscription`}
          description="Transform this accepted quotation into an active recurring subscription ledger."
        >
          <div className="space-y-4">
            <div className="p-3.5 rounded-xl bg-[#F2EDE6] border border-[#E2D9D0] space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-[#7A6860]">Total Contract Value:</span>
                <span className="font-mono font-bold text-[#1C1410]">
                  {formatCurrency(selectedQuoteForConvert.total_amount)}
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-[#7A6860]">Total Line Items:</span>
                <span className="font-mono text-[#1C1410]">
                  {selectedQuoteForConvert.items?.length || 0} Deliverables
                </span>
              </div>
            </div>

            <Select
              label="Select Target Recurring Plan"
              value={convertPlanId || ''}
              onChange={(e) => setConvertPlanId(Number(e.target.value))}
              options={(plans || []).map((p) => ({
                value: p.id,
                label: `${p.name} (${formatCurrency(p.base_price)} / ${p.billing_interval})`,
              }))}
              required
            />

            <Select
              label="Billing Cadence"
              value={convertBillingInterval}
              onChange={(e) => setConvertBillingInterval(e.target.value as any)}
              options={[
                { value: 'month', label: 'Monthly Invoicing' },
                { value: 'year', label: 'Annual Billing (365 days)' },
                { value: 'week', label: 'Weekly Cadence' },
              ]}
            />

            <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
              <Button variant="secondary" onClick={() => setIsConvertModalOpen(false)}>
                Cancel
              </Button>
              <Button
                variant="primary"
                loading={convertMutation.isPending}
                onClick={() => {
                  if (!convertPlanId) return;
                  convertMutation.mutate({
                    id: selectedQuoteForConvert.id,
                    data: {
                      plan_id: convertPlanId,
                      billing_interval: convertBillingInterval,
                    },
                  });
                }}
              >
                Confirm & Activate Subscription
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Create Quotation Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Draft Sales Quotation"
        description="Build an itemized deal proposal for an existing customer account."
        maxWidth="2xl"
      >
        <form onSubmit={handleCreateQuotation} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Customer Account"
              value={customerId || ''}
              onChange={(e) => setCustomerId(Number(e.target.value))}
              options={(customerList?.items || []).map((c) => ({
                value: c.id,
                label: `${c.name} (${c.customer_code})`,
              }))}
              required
            />
            <Input
              label="Currency"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              disabled
            />
          </div>

          {/* Dynamic Line Items */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#1C1410] uppercase tracking-wider">
                Quotation Line Items
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
                      placeholder="Line description"
                      value={item.description}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].description = e.target.value;
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
                      placeholder="Unit Price"
                      value={item.unit_price}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].unit_price = Number(e.target.value) || 0;
                        setItems(updated);
                      }}
                      required
                    />
                  </div>
                  <div className="col-span-2">
                    <Input
                      type="number"
                      min="0"
                      placeholder="GST %"
                      value={item.tax_rate_percent}
                      onChange={(e) => {
                        const updated = [...items];
                        updated[idx].tax_rate_percent = Number(e.target.value) || 0;
                        setItems(updated);
                      }}
                    />
                  </div>
                  <div className="col-span-1 text-center">
                    <button
                      type="button"
                      disabled={items.length <= 1}
                      onClick={() => handleRemoveItem(idx)}
                      className="text-[#7A6860] hover:text-[#8B1A1A] p-1 disabled:opacity-30"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Live Calculation Summary */}
          <div className="p-4 rounded-xl bg-[#F2EDE6] border border-[#E2D9D0] space-y-1.5 text-xs">
            <div className="flex justify-between text-[#7A6860]">
              <span>Subtotal:</span>
              <span className="font-mono text-[#1C1410]">{formatCurrency(calculatedSubtotal)}</span>
            </div>
            <div className="flex justify-between text-[#7A6860]">
              <span>Estimated Taxes (GST):</span>
              <span className="font-mono text-[#1C1410]">{formatCurrency(calculatedTax)}</span>
            </div>
            <div className="flex justify-between text-sm font-bold text-[#1C1410] pt-2 border-t border-[#E2D9D0]">
              <span>Total Quotation Amount:</span>
              <span className="font-mono text-[#6B1A2A]">{formatCurrency(calculatedTotal)}</span>
            </div>
          </div>

          <Input
            label="Payment & Contract Terms"
            value={terms}
            onChange={(e) => setTerms(e.target.value)}
          />

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Save Quotation Draft
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
