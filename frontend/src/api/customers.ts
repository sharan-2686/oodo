import { apiClient } from './client';
import { Customer, CustomerCreateInput, CustomerListResponse } from '../types';

export const customersApi = {
  list: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    is_active?: boolean;
  }): Promise<CustomerListResponse> => {
    const response = await apiClient.get<CustomerListResponse>('/customers', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Customer> => {
    const response = await apiClient.get<Customer>(`/customers/${id}`);
    return response.data;
  },

  create: async (data: CustomerCreateInput): Promise<Customer> => {
    const response = await apiClient.post<Customer>('/customers', data);
    return response.data;
  },

  update: async (id: number, data: Partial<CustomerCreateInput>): Promise<Customer> => {
    const response = await apiClient.put<Customer>(`/customers/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/customers/${id}`);
  },
};

