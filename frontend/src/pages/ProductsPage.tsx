import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { catalogApi } from '../api/catalog';
import { Product, ProductCreateInput } from '../types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { formatCurrency } from '../utils/formatters';
import { Plus, Layers, Tag } from 'lucide-react';

export const ProductsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [formData, setFormData] = useState<ProductCreateInput>({
    sku: `PRD-${Math.floor(100 + Math.random() * 900)}`,
    name: '',
    description: '',
    category: 'Software',
    is_active: true,
    variants: [
      {
        sku: `VAR-${Math.floor(100 + Math.random() * 900)}`,
        name: 'Standard License',
        unit_price: 999,
        currency: 'INR',
        is_active: true,
      },
    ],
  });
  const [formError, setFormError] = useState<string | null>(null);

  const { data: products, isLoading } = useQuery({
    queryKey: ['products'],
    queryFn: () => catalogApi.listProducts(),
  });

  const createMutation = useMutation({
    mutationFn: (data: ProductCreateInput) => catalogApi.createProduct(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      setIsModalOpen(false);
      resetForm();
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to create product');
    },
  });

  const resetForm = () => {
    setFormData({
      sku: `PRD-${Math.floor(100 + Math.random() * 900)}`,
      name: '',
      description: '',
      category: 'Software',
      is_active: true,
      variants: [
        {
          sku: `VAR-${Math.floor(100 + Math.random() * 900)}`,
          name: 'Standard License',
          unit_price: 999,
          currency: 'INR',
          is_active: true,
        },
      ],
    });
    setFormError(null);
  };

  const handleCreateProduct = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setFormError('Product title is required');
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
            Product & Variant Catalog
          </h2>
          <p className="text-xs text-[#7A6860] mt-1">
            Configure line item deliverables, SKU matrices, and pricing tiers.
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
          Add Product SKU
        </Button>
      </div>

      {/* Catalog Table */}
      {isLoading ? (
        <LoadingSpinner />
      ) : !products || products.length === 0 ? (
        <EmptyState
          title="No products configured"
          description="Build your product catalog to use items in quotes, plans, and invoices."
          actionLabel="Create Product"
          onAction={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        />
      ) : (
        <div className="space-y-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>SKU</TableHead>
                <TableHead>Product Name & Category</TableHead>
                <TableHead>Variants Count</TableHead>
                <TableHead>Starting Price</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {products.map((p) => {
                const minPrice = p.variants?.length
                  ? Math.min(...p.variants.map((v) => Number(v.unit_price)))
                  : 0;

                return (
                  <TableRow key={p.id}>
                    <TableCell className="font-mono text-[#6B1A2A] font-semibold">{p.sku}</TableCell>
                    <TableCell>
                      <div className="font-semibold text-[#1C1410]">{p.name}</div>
                      {p.description && (
                        <div className="text-xs text-[#7A6860] line-clamp-1">{p.description}</div>
                      )}
                      {p.category && (
                        <span className="inline-flex items-center gap-1 text-[10px] text-[#6B1A2A] font-mono mt-1">
                          <Tag className="w-2.5 h-2.5" /> {p.category}
                        </span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1 text-xs text-[#7A6860]">
                        <Layers className="w-3.5 h-3.5 text-[#6B1A2A]" />
                        <span>{p.variants?.length || 0} variant(s)</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-mono text-[#1C1410] font-medium">
                      {formatCurrency(minPrice)}
                    </TableCell>
                    <TableCell>
                      <Badge variant={p.is_active ? 'success' : 'default'} dot>
                        {p.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Create Product Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add Product & Variant"
        description="Introduce a new product SKU into the recurring billing catalog."
      >
        <form onSubmit={handleCreateProduct} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Product SKU"
              value={formData.sku}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              required
            />
            <Input
              label="Category"
              placeholder="e.g. SaaS, Add-on, Enterprise"
              value={formData.category || ''}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            />
          </div>

          <Input
            label="Product Title"
            placeholder="e.g. Cloud Telemetry Agent"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Input
            label="Description"
            placeholder="High-throughput realtime metrics engine"
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />

          {/* Initial Variant Setup */}
          <div className="p-4 rounded-xl bg-[#F2EDE6] border border-[#E2D9D0] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#1C1410]">Default Variant Configuration</span>
              <Badge variant="purple" className="text-[10px]">Variant 1</Badge>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Variant SKU"
                value={formData.variants?.[0]?.sku || ''}
                onChange={(e) => {
                  const vars = [...(formData.variants || [])];
                  vars[0] = { ...vars[0], sku: e.target.value };
                  setFormData({ ...formData, variants: vars });
                }}
                required
              />
              <Input
                label="Variant Name"
                value={formData.variants?.[0]?.name || ''}
                onChange={(e) => {
                  const vars = [...(formData.variants || [])];
                  vars[0] = { ...vars[0], name: e.target.value };
                  setFormData({ ...formData, variants: vars });
                }}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Unit Price (INR)"
                type="number"
                min="0"
                step="0.01"
                value={formData.variants?.[0]?.unit_price || 0}
                onChange={(e) => {
                  const vars = [...(formData.variants || [])];
                  vars[0] = { ...vars[0], unit_price: Number(e.target.value) };
                  setFormData({ ...formData, variants: vars });
                }}
                required
              />
              <Input
                label="Currency"
                value="INR"
                disabled
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Create Product SKU
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
