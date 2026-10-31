import { apiClient } from './client';
import { Payment, PaymentCreateInput } from '../types';

export const paymentsApi = {
  list: async (params?: { customer_id?: number; status?: string }): Promise<Payment[]> => {
    const response = await apiClient.get<Payment[]>('/payments', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Payment> => {
    const response = await apiClient.get<Payment>(`/payments/${id}`);
    return response.data;
  },

  record: async (data: PaymentCreateInput): Promise<Payment> => {
    const response = await apiClient.post<Payment>('/payments', data);
    return response.data;
  },

  create: async (data: PaymentCreateInput): Promise<Payment> => {
    const response = await apiClient.post<Payment>('/payments', data);
    return response.data;
  },
};

