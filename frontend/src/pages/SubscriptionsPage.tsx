import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { subscriptionsApi } from '../api/subscriptions';
import { invoicesApi } from '../api/invoices';
import { customersApi } from '../api/customers';
import { catalogApi } from '../api/catalog';
import { Subscription, SubscriptionCreateInput, SubscriptionStatusTransition } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatCurrency, formatDate, getStatusBadgeVariant } from '../utils/formatters';
import { Plus, Pause, Play, XOctagon, Receipt, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const SubscriptionsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isActionModalOpen, setIsActionModalOpen] = useState(false);
  const [selectedSubForAction, setSelectedSubForAction] = useState<Subscription | null>(null);
  const [actionType, setActionType] = useState<SubscriptionStatusTransition['action']>('pause');
  const [actionReason, setActionReason] = useState('');

  // Form State
  const [createCustomerId, setCreateCustomerId] = useState<number | undefined>(undefined);
  const [createPlanId, setCreatePlanId] = useState<number | undefined>(undefined);
  const [createBillingInterval, setCreateBillingInterval] = useState<'month' | 'year' | 'week' | 'day'>('month');
  const [formError, setFormError] = useState<string | null>(null);

  // Queries
  const { data: subscriptions, isLoading } = useQuery({
    queryKey: ['subscriptions'],
    queryFn: () => subscriptionsApi.list(),
  });

  const { data: customerList } = useQuery({
    queryKey: ['customers'],
    queryFn: () => customersApi.list({ limit: 100 }),
  });

  const { data: plans } = useQuery({
    queryKey: ['plans'],
    queryFn: () => catalogApi.listPlans(),
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: SubscriptionCreateInput) => subscriptionsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
      setIsCreateModalOpen(false);
      setFormError(null);
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to provision subscription');
    },
  });

  const lifecycleMutation = useMutation({
    mutationFn: ({ id, req }: { id: number; req: SubscriptionStatusTransition }) =>
      subscriptionsApi.transitionLifecycle(id, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subscriptions'] });
      setIsActionModalOpen(false);
      setSelectedSubForAction(null);
      setActionReason('');
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Action failed');
    },
  });

  const generateInvoiceMutation = useMutation({
    mutationFn: (subId: number) =>
      invoicesApi.generateFromSubscription({ subscription_id: subId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['invoices'] });
      navigate('/staff/invoices');
    },
    onError: (err: any) => {
      alert(err.response?.data?.detail || 'Invoice generation failed');
    },
  });

  const handleOpenActionModal = (sub: Subscription, action: SubscriptionStatusTransition['action']) => {
    setSelectedSubForAction(sub);
    setActionType(action);
    setActionReason('');
    setIsActionModalOpen(true);
  };

  const handleExecuteAction = () => {
    if (!selectedSubForAction) return;
    lifecycleMutation.mutate({
      id: selectedSubForAction.id,
      req: { action: actionType, reason: actionReason || undefined },
    });
  };

  const handleDirectCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!createCustomerId || !createPlanId) {
      setFormError('Customer and Plan are required');
      return;
    }
    createMutation.mutate({
      customer_id: createCustomerId,
      plan_id: createPlanId,
      billing_interval: createBillingInterval,
      interval_count: 1,
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[#1C1410] font-display flex items-center gap-2">
            Subscription Lifecycle Fleet
          </h2>
          <p className="text-xs text-[#7A6860] mt-1">
            Monitor active recurrent contracts, manage period transitions, and initiate automated billing runs.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            if (customerList?.items?.length) setCreateCustomerId(customerList.items[0].id);
            if (plans?.length) setCreatePlanId(plans[0].id);
            setIsCreateModalOpen(true);
          }}
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Provision Subscription
        </Button>
      </div>

      {/* Subscriptions Table */}
      {isLoading ? (
        <LoadingSpinner />
      ) : !subscriptions || subscriptions.length === 0 ? (
        <EmptyState
          title="No subscriptions active"
          description="Provision a subscription directly or convert an accepted quote to populate your recurring fleet."
          actionLabel="Provision Subscription"
          onAction={() => setIsCreateModalOpen(true)}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Subscription #</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Plan & Frequency</TableHead>
              <TableHead>Recurring Amount</TableHead>
              <TableHead>Next Billing Date</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Lifecycle Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {subscriptions.map((s) => {
              const statusBadge = getStatusBadgeVariant(s.status);
              const customerObj = customerList?.items?.find((c) => c.id === s.customer_id);
              const planObj = plans?.find((p) => p.id === s.plan_id);

              return (
                <TableRow key={s.id}>
                  <TableCell className="font-mono font-semibold text-[#6B1A2A]">
                    {s.subscription_number}
                  </TableCell>
                  <TableCell>
                    <div className="font-semibold text-[#1C1410]">
                      {customerObj?.name || `Customer #${s.customer_id}`}
                    </div>
                    {customerObj?.company_name && (
                      <div className="text-xs text-[#7A6860]">{customerObj.company_name}</div>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="text-[#1C1410] font-medium">{planObj?.name || `Plan #${s.plan_id}`}</div>
                    <div className="text-xs text-[#7A6860] capitalize">
                      Every {s.interval_count} {s.billing_interval}(s)
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-sm font-bold text-[#1C1410]">
                    {formatCurrency(s.unit_price)}
                  </TableCell>
                  <TableCell className="text-xs text-[#7A6860]">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-[#6B1A2A]" />
                      <span>{formatDate(s.next_billing_at || s.current_period_end)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusBadge.variant} dot>
                      {statusBadge.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {/* Generate Recurring Invoice */}
                      {(s.status === 'active' || s.status === 'trialing') && (
                        <Button
                          size="sm"
                          variant="secondary"
                          title="Generate Invoice for Period"
                          onClick={() => generateInvoiceMutation.mutate(s.id)}
                          loading={generateInvoiceMutation.isPending}
                        >
                          <Receipt className="w-3.5 h-3.5 mr-1 text-[#6B1A2A]" />
                          Bill
                        </Button>
                      )}

                      {/* Pause */}
                      {s.status === 'active' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          title="Pause Subscription"
                          onClick={() => handleOpenActionModal(s, 'pause')}
                        >
                          <Pause className="w-3.5 h-3.5 text-[#7B5E00]" />
                        </Button>
                      )}

                      {/* Resume */}
                      {s.status === 'paused' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          title="Resume Subscription"
                          onClick={() => handleOpenActionModal(s, 'resume')}
                        >
                          <Play className="w-3.5 h-3.5 mr-1 text-[#2D6A4F]" />
                          Resume
                        </Button>
                      )}

                      {/* Cancel */}
                      {s.status !== 'cancelled' && (
                        <Button
                          size="sm"
                          variant="secondary"
                          title="Cancel Subscription"
                          onClick={() => handleOpenActionModal(s, 'cancel')}
                          className="text-[#8B1A1A] border-[#FFC9C9]"
                        >
                          <XOctagon className="w-3.5 h-3.5" />
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

      {/* Lifecycle Action Confirmation Modal */}
      {isActionModalOpen && selectedSubForAction && (
        <Modal
          isOpen={isActionModalOpen}
          onClose={() => setIsActionModalOpen(false)}
          title={`Confirm Subscription Action: ${actionType.toUpperCase()}`}
          description={`Subscription ${selectedSubForAction.subscription_number}`}
        >
          <div className="space-y-4">
            <p className="text-xs text-[#7A6860] leading-relaxed">
              Are you sure you want to transition this subscription to <strong>{actionType}</strong>? This will update the state machine and create an immutable lifecycle audit event.
            </p>

            <Input
              label="Action Reason (Optional)"
              placeholder="e.g. Customer requested temporary seasonal freeze"
              value={actionReason}
              onChange={(e) => setActionReason(e.target.value)}
            />

            <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
              <Button variant="secondary" onClick={() => setIsActionModalOpen(false)}>
                Cancel
              </Button>
              <Button
                variant={actionType === 'cancel' ? 'danger' : 'primary'}
                loading={lifecycleMutation.isPending}
                onClick={handleExecuteAction}
              >
                Confirm {actionType.toUpperCase()}
              </Button>
            </div>
          </div>
        </Modal>
      )}

      {/* Direct Provisioning Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Direct Provision Subscription"
        description="Attach an active customer account directly to a subscription plan."
      >
        <form onSubmit={handleDirectCreate} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <Select
            label="Customer Account"
            value={createCustomerId || ''}
            onChange={(e) => setCreateCustomerId(Number(e.target.value))}
            options={(customerList?.items || []).map((c) => ({
              value: c.id,
              label: `${c.name} (${c.customer_code})`,
            }))}
            required
          />

          <Select
            label="Subscription Plan"
            value={createPlanId || ''}
            onChange={(e) => setCreatePlanId(Number(e.target.value))}
            options={(plans || []).map((p) => ({
              value: p.id,
              label: `${p.name} (${formatCurrency(p.base_price)} / ${p.billing_interval})`,
            }))}
            required
          />

          <Select
            label="Billing Interval"
            value={createBillingInterval}
            onChange={(e) => setCreateBillingInterval(e.target.value as any)}
            options={[
              { value: 'month', label: 'Monthly' },
              { value: 'year', label: 'Yearly' },
              { value: 'week', label: 'Weekly' },
              { value: 'day', label: 'Daily' },
            ]}
          />

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Provision & Activate
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
