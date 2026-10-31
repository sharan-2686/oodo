import { apiClient } from './client';
import {
  Invoice,
  InvoiceCreateOneTimeInput,
  InvoiceGenerateFromSubscriptionInput,
} from '../types';

export const invoicesApi = {
  list: async (params?: { customer_id?: number; subscription_id?: number; status?: string }): Promise<Invoice[]> => {
    const response = await apiClient.get<Invoice[]>('/invoices', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Invoice> => {
    const response = await apiClient.get<Invoice>(`/invoices/${id}`);
    return response.data;
  },

  createOneTime: async (data: InvoiceCreateOneTimeInput): Promise<Invoice> => {
    const response = await apiClient.post<Invoice>('/invoices', data);
    return response.data;
  },

  generateFromSubscription: async (data: InvoiceGenerateFromSubscriptionInput): Promise<Invoice> => {
    const response = await apiClient.post<Invoice>('/invoices/generate-from-subscription', data);
    return response.data;
  },

  executeAction: async (id: number, action: string, notes?: string): Promise<Invoice> => {
    const response = await apiClient.post<Invoice>(`/invoices/${id}/actions`, {
      action,
      notes,
    });
    return response.data;
  },
};

