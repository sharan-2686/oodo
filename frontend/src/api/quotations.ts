import { apiClient } from './client';
import {
  Quotation,
  QuotationCreateInput,
  QuotationConvertRequest,
  Subscription,
} from '../types';

export const quotationsApi = {
  list: async (params?: { customer_id?: number; status?: string }): Promise<Quotation[]> => {
    const response = await apiClient.get<Quotation[]>('/quotations', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Quotation> => {
    const response = await apiClient.get<Quotation>(`/quotations/${id}`);
    return response.data;
  },

  create: async (data: QuotationCreateInput): Promise<Quotation> => {
    const response = await apiClient.post<Quotation>('/quotations', data);
    return response.data;
  },

  updateStatus: async (id: number, status: string): Promise<Quotation> => {
    const response = await apiClient.post<Quotation>(`/quotations/${id}/status`, null, {
      params: { status_value: status },
    });
    return response.data;
  },

  convertToSubscription: async (id: number, data: QuotationConvertRequest): Promise<Subscription> => {
    const response = await apiClient.post<Subscription>(`/quotations/${id}/convert`, data);
    return response.data;
  },
};

