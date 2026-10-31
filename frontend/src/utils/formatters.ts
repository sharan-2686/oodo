export function formatCurrency(amount: number | string | null | undefined, currency: string = 'INR'): string {
  if (amount === null || amount === undefined || isNaN(Number(amount))) return '₹0.00';
  const val = Number(amount);
  
  if (currency.toUpperCase() === 'INR') {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(val);
  }
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 2,
  }).format(val);
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return new Intl.DateTimeFormat('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(d);
  } catch {
    return dateStr;
  }
}

export function formatDateTime(dateTimeStr: string | null | undefined): string {
  if (!dateTimeStr) return '—';
  try {
    const d = new Date(dateTimeStr);
    return new Intl.DateTimeFormat('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  } catch {
    return dateTimeStr;
  }
}

export function getStatusBadgeVariant(status: string): {
  variant: 'success' | 'warning' | 'danger' | 'info' | 'default';
  label: string;
} {
  const s = status?.toLowerCase() || '';
  
  switch (s) {
    case 'active':
    case 'succeeded':
    case 'paid':
    case 'accepted':
    case 'converted':
      return { variant: 'success', label: status.toUpperCase() };

    case 'trialing':
    case 'pending':
    case 'sent':
    case 'draft':
      return { variant: 'warning', label: status.toUpperCase() };

    case 'past_due':
    case 'overdue':
    case 'failed':
    case 'rejected':
      return { variant: 'danger', label: status.replace('_', ' ').toUpperCase() };

    case 'paused':
      return { variant: 'info', label: 'PAUSED' };

    case 'cancelled':
    case 'expired':
    case 'void':
    default:
      return { variant: 'default', label: (status || 'UNKNOWN').toUpperCase() };
  }
}

