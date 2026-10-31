import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { Plan, PlanCreateInput } from '../types';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatCurrency } from '../utils/formatters';
import { Plus, Calendar, Clock, Check } from 'lucide-react';

export const PlansPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [formData, setFormData] = useState<PlanCreateInput>({
    code: `PLAN-${Math.floor(100 + Math.random() * 900)}`,
    name: '',
    description: '',
    billing_interval: 'month',
    interval_count: 1,
    base_price: 2499,
    currency: 'INR',
    trial_days: 14,
    is_active: true,
  });
  const [formError, setFormError] = useState<string | null>(null);

  const { data: plans, isLoading } = useQuery({
    queryKey: ['plans'],
    queryFn: () => catalogApi.listPlans(),
  });

  const createMutation = useMutation({
    mutationFn: (data: PlanCreateInput) => catalogApi.createPlan(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
      setIsModalOpen(false);
      resetForm();
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to create plan');
    },
  });

  const resetForm = () => {
    setFormData({
      code: `PLAN-${Math.floor(100 + Math.random() * 900)}`,
      name: '',
      description: '',
      billing_interval: 'month',
      interval_count: 1,
      base_price: 2499,
      currency: 'INR',
      trial_days: 14,
      is_active: true,
    });
    setFormError(null);
  };

  const handleCreatePlan = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setFormError('Plan title is required');
      return;
    }
    createMutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[#1C1410] font-display flex items-center gap-2">
            Recurring Plans & Pricing Tiers
          </h2>
          <p className="text-xs text-[#7A6860] mt-1">
            Define recurring subscription intervals, trial windows, and automated billing amounts.
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        >
          <Plus className="w-4 h-4 mr-1.5" />
          Add Subscription Plan
        </Button>
      </div>

      {/* Plans Grid (Glass Cards) */}
      {isLoading ? (
        <LoadingSpinner />
      ) : !plans || plans.length === 0 ? (
        <EmptyState
          title="No subscription plans configured"
          description="Create recurring plans to begin selling subscription packages and automated billing runs."
          actionLabel="Create Plan"
          onAction={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {plans.map((p) => (
            <Card key={p.id} interactive className="flex flex-col justify-between">
              <div>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-[#6B1A2A] font-bold">{p.code}</span>
                    <Badge variant={p.is_active ? 'success' : 'default'} dot>
                      {p.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl mt-2">{p.name}</CardTitle>
                  <CardDescription className="line-clamp-2 mt-1">
                    {p.description || 'Enterprise recurring plan with automated billing engine integration.'}
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-extrabold font-mono tabular-nums text-[#1C1410]">
                      {formatCurrency(p.base_price)}
                    </span>
                    <span className="text-xs text-[#7A6860]">
                      / {p.interval_count > 1 ? `${p.interval_count} ` : ''}{p.billing_interval}
                    </span>
                  </div>

                  <div className="space-y-2 pt-2 border-t border-[#E2D9D0] text-xs text-[#1C1410]">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-[#6B1A2A]" />
                      <span>
                        Billed every {p.interval_count} {p.billing_interval}(s)
                      </span>
                    </div>
                    {p.trial_days > 0 && (
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4 text-[#C9A84C]" />
                        <span>{p.trial_days}-day complimentary trial period</span>
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-[#2D6A4F]" />
                      <span>{p.items?.length || 0} bundled catalog items</span>
                    </div>
                  </div>
                </CardContent>
              </div>

              <CardFooter className="justify-between text-xs text-[#7A6860]">
                <span>Currency: {p.currency}</span>
                <span className="font-mono">ID #{p.id}</span>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}

      {/* Create Plan Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Configure New Subscription Plan"
        description="Establish recurring cadence, base price, and trial eligibility."
      >
        <form onSubmit={handleCreatePlan} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Plan Code"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              required
            />
            <Input
              label="Plan Display Name"
              placeholder="e.g. Pro Growth Plan"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <Input
            label="Plan Description"
            placeholder="Comprehensive billing tier with priority support"
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Billing Interval"
              value={formData.billing_interval}
              onChange={(e) => setFormData({ ...formData, billing_interval: e.target.value as any })}
              options={[
                { value: 'day', label: 'Daily' },
                { value: 'week', label: 'Weekly' },
                { value: 'month', label: 'Monthly' },
                { value: 'year', label: 'Yearly' },
              ]}
            />
            <Input
              label="Interval Multiplier"
              type="number"
              min="1"
              value={formData.interval_count}
              onChange={(e) => setFormData({ ...formData, interval_count: parseInt(e.target.value) || 1 })}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Base Price (INR)"
              type="number"
              min="0"
              step="0.01"
              value={formData.base_price}
              onChange={(e) => setFormData({ ...formData, base_price: parseFloat(e.target.value) || 0 })}
              required
            />
            <Input
              label="Trial Days"
              type="number"
              min="0"
              value={formData.trial_days}
              onChange={(e) => setFormData({ ...formData, trial_days: parseInt(e.target.value) || 0 })}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Save Plan
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
