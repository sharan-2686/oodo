import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { customersApi } from '../api/customers';
import { Customer, CustomerCreateInput } from '../types';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Select } from '../components/ui/Select';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '../components/ui/Table';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { Plus, Search, Building2, Phone, Mail } from 'lucide-react';

export const CustomersPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);

  // Form State
  const [formData, setFormData] = useState<CustomerCreateInput>({
    customer_code: `CUST-${Math.floor(1000 + Math.random() * 9000)}`,
    customer_type: 'business',
    name: '',
    email: '',
    phone: '',
    company_name: '',
    tax_identifier: '',
    billing_address_line1: '',
    billing_city: '',
    billing_state: '',
    billing_postal_code: '',
    billing_country: 'IN',
  });
  const [formError, setFormError] = useState<string | null>(null);

  const { data: customerList, isLoading } = useQuery({
    queryKey: ['customers', search],
    queryFn: () => customersApi.list({ search: search || undefined, limit: 100 }),
  });

  const createMutation = useMutation({
    mutationFn: (data: CustomerCreateInput) => customersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
      setIsModalOpen(false);
      resetForm();
    },
    onError: (err: any) => {
      setFormError(err.response?.data?.detail || 'Failed to create customer');
    },
  });

  const resetForm = () => {
    setFormData({
      customer_code: `CUST-${Math.floor(1000 + Math.random() * 9000)}`,
      customer_type: 'business',
      name: '',
      email: '',
      phone: '',
      company_name: '',
      tax_identifier: '',
      billing_address_line1: '',
      billing_city: '',
      billing_state: '',
      billing_postal_code: '',
      billing_country: 'IN',
    });
    setFormError(null);
  };

  const handleCreateCustomer = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setFormError('Customer name is required');
      return;
    }
    createMutation.mutate(formData);
  };

  const filteredItems = (customerList?.items || []).filter((item) => {
    if (filterType === 'all') return true;
    return item.customer_type === filterType;
  });

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[#1C1410] font-display flex items-center gap-2">
            Customer Directory (360 Accounts)
          </h2>
          <p className="text-xs text-[#7A6860] mt-1">
            Manage individual and enterprise profiles, tax registrations, and billing addresses.
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
          Add New Customer
        </Button>
      </div>

      {/* Filter and Search Bar */}
      <Card className="p-4 border-[#E2D9D0]">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <div className="w-full sm:flex-1 relative">
            <Search className="w-4 h-4 text-[#7A6860] absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              className="form-input pl-9"
              placeholder="Search by code, customer name, company, or tax ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-48">
            <Select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              options={[
                { value: 'all', label: 'All Customer Types' },
                { value: 'business', label: 'Business (B2B)' },
                { value: 'individual', label: 'Individual (B2C)' },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* Customer Data Table */}
      {isLoading ? (
        <LoadingSpinner />
      ) : filteredItems.length === 0 ? (
        <EmptyState
          title="No customers found"
          description={
            search
              ? `No customer records matched "${search}".`
              : 'Get started by creating your first business or individual customer account.'
          }
          actionLabel="Create Customer"
          onAction={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Customer Code</TableHead>
              <TableHead>Client & Entity</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Contact & Tax ID</TableHead>
              <TableHead>Billing Location</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((c) => (
              <TableRow key={c.id}>
                <TableCell className="font-mono text-[#6B1A2A] font-semibold">
                  {c.customer_code}
                </TableCell>
                <TableCell>
                  <div className="font-semibold text-[#1C1410]">{c.name}</div>
                  {c.company_name && (
                    <div className="text-xs text-[#7A6860] flex items-center gap-1 mt-0.5">
                      <Building2 className="w-3 h-3 text-[#7A6860]" />
                      {c.company_name}
                    </div>
                  )}
                </TableCell>
                <TableCell>
                  <Badge variant={c.customer_type === 'business' ? 'purple' : 'default'} className="text-[10px]">
                    {c.customer_type}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="space-y-0.5 text-xs">
                    {c.email && (
                      <div className="flex items-center gap-1.5 text-[#1C1410]">
                        <Mail className="w-3 h-3 text-[#7A6860]" /> {c.email}
                      </div>
                    )}
                    {c.phone && (
                      <div className="flex items-center gap-1.5 text-[#7A6860]">
                        <Phone className="w-3 h-3 text-[#7A6860]" /> {c.phone}
                      </div>
                    )}
                    {c.tax_identifier && (
                      <div className="font-mono text-[11px] text-[#6B1A2A]">
                        GST: {c.tax_identifier}
                      </div>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <span className="text-xs text-[#7A6860]">
                    {[c.billing_city, c.billing_state, c.billing_country].filter(Boolean).join(', ') || '—'}
                  </span>
                </TableCell>
                <TableCell>
                  <Badge variant={c.is_active ? 'success' : 'default'} dot>
                    {c.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => setSelectedCustomer(c)}
                  >
                    View 360
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {/* Customer 360 Detail Modal */}
      {selectedCustomer && (
        <Modal
          isOpen={!!selectedCustomer}
          onClose={() => setSelectedCustomer(null)}
          title={`Customer 360: ${selectedCustomer.name}`}
          description={`Customer Code: ${selectedCustomer.customer_code} • Account ID #${selectedCustomer.id}`}
          maxWidth="2xl"
        >
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 p-4 rounded-xl bg-[#F2EDE6] border border-[#E2D9D0]">
              <div>
                <p className="text-[10px] uppercase text-[#7A6860] font-semibold">Account Type</p>
                <Badge variant="purple" className="mt-1">{selectedCustomer.customer_type}</Badge>
              </div>
              <div>
                <p className="text-[10px] uppercase text-[#7A6860] font-semibold">Company Name</p>
                <p className="text-xs text-[#1C1410] mt-1 font-medium">{selectedCustomer.company_name || 'N/A'}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-[#7A6860] font-semibold">Tax / GST Number</p>
                <p className="text-xs font-mono text-[#6B1A2A] font-semibold mt-1">{selectedCustomer.tax_identifier || 'None'}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-[#7A6860] font-semibold">Email</p>
                <p className="text-xs text-[#1C1410] mt-1">{selectedCustomer.email || '—'}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-[#7A6860] font-semibold">Phone</p>
                <p className="text-xs text-[#1C1410] mt-1">{selectedCustomer.phone || '—'}</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-[#7A6860] font-semibold">Status</p>
                <Badge variant={selectedCustomer.is_active ? 'success' : 'default'} dot className="mt-1">
                  {selectedCustomer.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>

            <div>
              <p className="text-xs font-semibold text-[#1C1410] uppercase tracking-wider mb-2">Registered Billing Address</p>
              <div className="p-3.5 rounded-lg bg-[#FAF7F2] border border-[#E2D9D0] text-xs text-[#1C1410] space-y-1">
                <p>{selectedCustomer.billing_address_line1 || 'No street address specified'}</p>
                {selectedCustomer.billing_address_line2 && <p>{selectedCustomer.billing_address_line2}</p>}
                <p>
                  {[selectedCustomer.billing_city, selectedCustomer.billing_state, selectedCustomer.billing_postal_code, selectedCustomer.billing_country]
                    .filter(Boolean)
                    .join(', ')}
                </p>
              </div>
            </div>

            {selectedCustomer.notes && (
              <div>
                <p className="text-xs font-semibold text-[#1C1410] uppercase tracking-wider mb-1">Internal Notes</p>
                <p className="text-xs text-[#7A6860] p-3 rounded-lg bg-[#FAF7F2] border border-[#E2D9D0]">
                  {selectedCustomer.notes}
                </p>
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Create Customer Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Register New Customer"
        description="Add a new business or individual customer profile to Brightloop 360."
        maxWidth="xl"
      >
        <form onSubmit={handleCreateCustomer} className="space-y-4">
          {formError && (
            <div className="p-3 rounded-lg bg-[#FFE5E5] border border-[#8B1A1A]/30 text-xs text-[#8B1A1A]">
              {formError}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Customer Code"
              value={formData.customer_code}
              onChange={(e) => setFormData({ ...formData, customer_code: e.target.value })}
              required
            />
            <Select
              label="Account Type"
              value={formData.customer_type}
              onChange={(e) => setFormData({ ...formData, customer_type: e.target.value as any })}
              options={[
                { value: 'business', label: 'Business / Enterprise' },
                { value: 'individual', label: 'Individual Consumer' },
              ]}
            />
          </div>

          <Input
            label="Legal / Display Name"
            placeholder="e.g. Acme Technologies Pvt Ltd"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Company Name (Optional)"
              placeholder="e.g. Acme Corp"
              value={formData.company_name || ''}
              onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
            />
            <Input
              label="Tax Identifier / GST"
              placeholder="e.g. 29AAAAA0000A1Z5"
              value={formData.tax_identifier || ''}
              onChange={(e) => setFormData({ ...formData, tax_identifier: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Primary Email"
              type="email"
              placeholder="billing@acme.com"
              value={formData.email || ''}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            />
            <Input
              label="Phone Number"
              placeholder="+91 98765 43210"
              value={formData.phone || ''}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            />
          </div>

          <Input
            label="Billing Street Address"
            placeholder="Level 4, Tech Park, Industrial Area"
            value={formData.billing_address_line1 || ''}
            onChange={(e) => setFormData({ ...formData, billing_address_line1: e.target.value })}
          />

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="City"
              placeholder="Bengaluru"
              value={formData.billing_city || ''}
              onChange={(e) => setFormData({ ...formData, billing_city: e.target.value })}
            />
            <Input
              label="State / Province"
              placeholder="Karnataka"
              value={formData.billing_state || ''}
              onChange={(e) => setFormData({ ...formData, billing_state: e.target.value })}
            />
            <Input
              label="Postal Code"
              placeholder="560100"
              value={formData.billing_postal_code || ''}
              onChange={(e) => setFormData({ ...formData, billing_postal_code: e.target.value })}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-[#E2D9D0]">
            <Button type="button" variant="secondary" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={createMutation.isPending}>
              Create Customer
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
