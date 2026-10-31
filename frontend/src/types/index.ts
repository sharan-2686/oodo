// --- Auth & Identity ---
export interface Permission {
  id: number;
  code: string;
  description?: string;
}

export interface Role {
  id: number;
  name: string;
  description?: string;
  permissions: string[];
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  is_active: boolean;
  role: Role;
  permissions: string[];
  last_login_at?: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// --- Customer ---
export interface Customer {
  id: number;
  customer_code: string;
  customer_type: 'individual' | 'business';
  name: string;
  email?: string;
  phone?: string;
  company_name?: string;
  tax_identifier?: string;
  billing_address_line1?: string;
  billing_address_line2?: string;
  billing_city?: string;
  billing_state?: string;
  billing_postal_code?: string;
  billing_country?: string;
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CustomerListResponse {
  total: number;
  items: Customer[];
}

export interface CustomerCreateInput {
  customer_code: string;
  customer_type?: 'individual' | 'business';
  name: string;
  email?: string;
  phone?: string;
  company_name?: string;
  tax_identifier?: string;
  billing_address_line1?: string;
  billing_address_line2?: string;
  billing_city?: string;
  billing_state?: string;
  billing_postal_code?: string;
  billing_country?: string;
  notes?: string;
  is_active?: boolean;
}

// --- Catalog & Plans ---
export interface ProductVariant {
  id: number;
  product_id: number;
  sku: string;
  name: string;
  attributes?: Record<string, any>;
  unit_price: number | string;
  currency: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  sku: string;
  name: string;
  description?: string;
  category?: string;
  is_active: boolean;
  variants: ProductVariant[];
  created_at: string;
  updated_at: string;
}

export interface ProductCreateInput {
  sku: string;
  name: string;
  description?: string;
  category?: string;
  is_active?: boolean;
  variants?: Array<{
    sku: string;
    name: string;
    attributes?: Record<string, any>;
    unit_price: number;
    currency?: string;
    is_active?: boolean;
  }>;
}

export interface PlanItem {
  id: number;
  plan_id: number;
  product_id: number;
  variant_id?: number;
  quantity: number | string;
  unit_price: number | string;
  created_at: string;
}

export interface Plan {
  id: number;
  code: string;
  name: string;
  description?: string;
  billing_interval: 'day' | 'week' | 'month' | 'year';
  interval_count: number;
  base_price: number | string;
  currency: string;
  trial_days: number;
  is_active: boolean;
  items: PlanItem[];
  created_at: string;
  updated_at: string;
}

export interface PlanCreateInput {
  code: string;
  name: string;
  description?: string;
  billing_interval?: 'day' | 'week' | 'month' | 'year';
  interval_count?: number;
  base_price?: number;
  currency?: string;
  trial_days?: number;
  is_active?: boolean;
  items?: Array<{
    product_id: number;
    variant_id?: number;
    quantity: number;
    unit_price: number;
  }>;
}

// --- Taxes & Discounts ---
export interface TaxRate {
  id: number;
  name: string;
  code: string;
  rate_percent: number | string;
  country?: string;
  region?: string;
  is_inclusive: boolean;
  is_active: boolean;
  effective_from?: string;
  effective_to?: string;
}

export interface Discount {
  id: number;
  code: string;
  name: string;
  discount_type: 'percentage' | 'fixed';
  discount_value: number | string;
  currency?: string;
  starts_at?: string;
  ends_at?: string;
  max_redemptions?: number;
  redemption_count?: number;
  is_active: boolean;
}

// --- Quotations ---
export interface QuotationItem {
  id: number;
  quotation_id: number;
  product_id?: number;
  variant_id?: number;
  plan_id?: number;
  description: string;
  quantity: number | string;
  unit_price: number | string;
  tax_rate_percent: number | string;
  line_subtotal: number | string;
  line_tax: number | string;
  line_total: number | string;
}

export interface Quotation {
  id: number;
  quote_number: string;
  customer_id: number;
  created_by?: number;
  discount_id?: number;
  status: 'draft' | 'sent' | 'accepted' | 'rejected' | 'expired' | 'converted';
  issue_date: string;
  valid_until?: string;
  currency: string;
  subtotal: number | string;
  discount_amount: number | string;
  tax_amount: number | string;
  total_amount: number | string;
  terms?: string;
  notes?: string;
  items: QuotationItem[];
  created_at: string;
  updated_at: string;
}

export interface QuotationCreateInput {
  customer_id?: number;
  discount_id?: number;
  issue_date?: string;
  valid_until?: string;
  currency?: string;
  terms?: string;
  notes?: string;
  items: Array<{
    product_id?: number;
    variant_id?: number;
    plan_id?: number;
    description: string;
    quantity: number;
    unit_price: number;
    tax_rate_percent?: number;
  }>;
}

export interface QuotationConvertRequest {
  plan_id?: number;
  start_date?: string;
  billing_interval?: 'day' | 'week' | 'month' | 'year';
  payment_terms?: string;
}

// --- Subscriptions ---
export interface SubscriptionItem {
  id: number;
  subscription_id: number;
  product_id: number;
  variant_id?: number;
  description_snapshot: string;
  quantity: number | string;
  unit_price: number | string;
  created_at: string;
}

export interface SubscriptionEvent {
  id: number;
  subscription_id: number;
  event_type: string;
  from_status?: string;
  to_status?: string;
  event_data?: Record<string, any>;
  actor_user_id?: number;
  created_at: string;
}

export interface Subscription {
  id: number;
  subscription_number: string;
  customer_id: number;
  plan_id: number;
  quotation_id?: number;
  discount_id?: number;
  status: 'draft' | 'trialing' | 'active' | 'past_due' | 'paused' | 'cancelled' | 'expired';
  currency: string;
  unit_price: number | string;
  quantity: number | string;
  billing_interval: 'day' | 'week' | 'month' | 'year';
  interval_count: number;
  start_date: string;
  trial_ends_at?: string;
  current_period_start?: string;
  current_period_end?: string;
  next_billing_at?: string;
  cancel_at_period_end: boolean;
  cancelled_at?: string;
  created_by?: number;
  items: SubscriptionItem[];
  events: SubscriptionEvent[];
  created_at: string;
  updated_at: string;
}

export interface SubscriptionCreateInput {
  customer_id: number;
  plan_id: number;
  quotation_id?: number;
  discount_id?: number;
  unit_price?: number;
  quantity?: number;
  billing_interval?: 'day' | 'week' | 'month' | 'year';
  interval_count?: number;
  start_date?: string;
}

export interface SubscriptionStatusTransition {
  action: 'confirm' | 'activate' | 'pause' | 'resume' | 'cancel' | 'close' | 'renew';
  reason?: string;
}

// --- Invoices ---
export interface InvoiceItem {
  id: number;
  invoice_id: number;
  product_id?: number;
  variant_id?: number;
  plan_id?: number;
  description_snapshot: string;
  sku_snapshot?: string;
  quantity: number | string;
  unit_price: number | string;
  tax_rate_id?: number;
  tax_name_snapshot?: string;
  tax_rate_percent: number | string;
  line_subtotal: number | string;
  line_tax: number | string;
  line_total: number | string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  customer_id: number;
  subscription_id?: number;
  discount_id?: number;
  invoice_type: 'subscription' | 'one_time' | 'adjustment';
  status: 'draft' | 'issued' | 'partially_paid' | 'paid' | 'overdue' | 'void' | 'uncollectible';
  currency: string;
  issue_date: string;
  due_date: string;
  billing_period_start?: string;
  billing_period_end?: string;
  subtotal: number | string;
  discount_amount: number | string;
  tax_amount: number | string;
  total_amount: number | string;
  amount_paid: number | string;
  balance_due: number | string;
  discount_code_snapshot?: string;
  customer_name_snapshot: string;
  customer_email_snapshot?: string;
  billing_address_snapshot?: Record<string, any>;
  notes?: string;
  created_by?: number;
  items: InvoiceItem[];
  created_at: string;
  updated_at: string;
}

export interface InvoiceCreateOneTimeInput {
  customer_id: number;
  discount_id?: number;
  issue_date?: string;
  due_date?: string;
  currency?: string;
  notes?: string;
  items: Array<{
    description_snapshot: string;
    quantity: number;
    unit_price: number;
    tax_rate_percent?: number;
    tax_name_snapshot?: string;
    product_id?: number;
    variant_id?: number;
  }>;
}

export interface InvoiceGenerateFromSubscriptionInput {
  subscription_id: number;
  billing_period_start?: string;
  billing_period_end?: string;
  issue_date?: string;
  due_date?: string;
}

// --- Payments ---
export interface PaymentAllocation {
  id: number;
  payment_id: number;
  invoice_id: number;
  amount_allocated: number | string;
  created_at: string;
}

export interface Payment {
  id: number;
  payment_number: string;
  customer_id: number;
  amount: number | string;
  currency: string;
  payment_method: 'cash' | 'bank_transfer' | 'card' | 'upi' | 'gateway' | 'other';
  status: 'pending' | 'succeeded' | 'failed' | 'refunded' | 'partially_refunded';
  transaction_reference?: string;
  idempotency_key?: string;
  paid_at?: string;
  notes?: string;
  total_allocated: number | string;
  unallocated_amount: number | string;
  allocations: PaymentAllocation[];
  created_at: string;
}

export interface PaymentCreateInput {
  customer_id: number;
  amount: number;
  currency?: string;
  payment_method?: 'cash' | 'bank_transfer' | 'card' | 'upi' | 'gateway' | 'other';
  transaction_reference?: string;
  idempotency_key?: string;
  paid_at?: string;
  notes?: string;
  allocations?: Array<{
    invoice_id: number;
    amount: number;
  }>;
}

// --- Dashboard ---
export interface OverdueInvoiceItem {
  id: number;
  invoice_number: string;
  customer_id: number;
  customer_name: string;
  issue_date: string;
  due_date: string;
  total_amount: number | string;
  amount_paid: number | string;
  balance_due: number | string;
  days_overdue: number;
}

export interface DashboardSummary {
  active_subscriptions_count: number;
  total_revenue_collected: number | string;
  total_revenue_owed: number | string;
  total_invoices_count: number;
  overdue_invoices_count: number;
  overdue_invoices: OverdueInvoiceItem[];
  subscriptions_by_status: Record<string, number>;
}

