import { apiClient } from './client';

export interface RazorpayOrderResponse {
  razorpay_order_id: string;
  razorpay_key_id: string;
  amount: number;
  currency: string;
  invoice_number: string;
  customer_name: string;
  customer_email: string;
}

export interface RazorpayVerifyPayload {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
  invoice_id: number;
}

export const razorpayApi = {
  createOrder: async (invoiceId: number): Promise<RazorpayOrderResponse> => {
    const { data } = await apiClient.post<RazorpayOrderResponse>('/payments/razorpay/order', {
      invoice_id: invoiceId,
    });
    return data;
  },

  verifyPayment: async (payload: RazorpayVerifyPayload): Promise<{ success: boolean; payment_id: number }> => {
    const { data } = await apiClient.post('/payments/razorpay/verify', payload);
    return data;
  },
};

declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    Razorpay: any;
  }
}

export function loadRazorpayScript(): Promise<boolean> {
  return new Promise((resolve) => {
    if (window.Razorpay) { resolve(true); return; }
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);
    document.body.appendChild(script);
  });
}

export interface RazorpayCheckoutOptions {
  keyId: string;
  orderId: string;
  amount: number;
  currency: string;
  description: string;
  customerName: string;
  customerEmail: string;
  customerPhone?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onSuccess: (response: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) => void;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onError: (error: any) => void;
  onDismiss: () => void;
}

export async function openRazorpayCheckout(options: RazorpayCheckoutOptions): Promise<void> {
  const loaded = await loadRazorpayScript();
  if (!loaded) throw new Error('Razorpay SDK failed to load. Check network connection.');

  const rzp = new window.Razorpay({
    key: options.keyId,
    order_id: options.orderId,
    amount: options.amount,
    currency: options.currency,
    name: 'Brightloop 360',
    description: options.description,
    prefill: {
      name: options.customerName,
      email: options.customerEmail,
      contact: options.customerPhone,
    },
    theme: { color: '#6B1A2A' },
    modal: { ondismiss: options.onDismiss },
    handler: options.onSuccess,
  });
  rzp.on('payment.failed', options.onError);
  rzp.open();
}

