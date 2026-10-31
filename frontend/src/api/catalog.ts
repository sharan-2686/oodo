import { apiClient } from './client';
import {
  Product,
  ProductCreateInput,
  Plan,
  PlanCreateInput,
  TaxRate,
  Discount,
} from '../types';

export const catalogApi = {
  // Products
  listProducts: async (params?: { category?: string; is_active?: boolean }): Promise<Product[]> => {
    const response = await apiClient.get<Product[]>('/products', { params });
    return response.data;
  },

  getProduct: async (id: number): Promise<Product> => {
    const response = await apiClient.get<Product>(`/products/${id}`);
    return response.data;
  },

  createProduct: async (data: ProductCreateInput): Promise<Product> => {
    const response = await apiClient.post<Product>('/products', data);
    return response.data;
  },

  updateProduct: async (id: number, data: Partial<ProductCreateInput>): Promise<Product> => {
    const response = await apiClient.put<Product>(`/products/${id}`, data);
    return response.data;
  },

  deleteProduct: async (id: number): Promise<void> => {
    await apiClient.delete(`/products/${id}`);
  },

  // Plans
  listPlans: async (params?: { billing_interval?: string; is_active?: boolean }): Promise<Plan[]> => {
    const response = await apiClient.get<Plan[]>('/plans', { params });
    return response.data;
  },

  getPlan: async (id: number): Promise<Plan> => {
    const response = await apiClient.get<Plan>(`/plans/${id}`);
    return response.data;
  },

  createPlan: async (data: PlanCreateInput): Promise<Plan> => {
    const response = await apiClient.post<Plan>('/plans', data);
    return response.data;
  },

  updatePlan: async (id: number, data: Partial<PlanCreateInput>): Promise<Plan> => {
    const response = await apiClient.put<Plan>(`/plans/${id}`, data);
    return response.data;
  },

  deletePlan: async (id: number): Promise<void> => {
    await apiClient.delete(`/plans/${id}`);
  },

  // Tax Rates
  listTaxes: async (params?: { is_active?: boolean; country?: string }): Promise<TaxRate[]> => {
    const response = await apiClient.get<TaxRate[]>('/taxes', { params });
    return response.data;
  },

  createTax: async (data: Partial<TaxRate>): Promise<TaxRate> => {
    const response = await apiClient.post<TaxRate>('/taxes', data);
    return response.data;
  },

  // Discounts
  listDiscounts: async (params?: { is_active?: boolean }): Promise<Discount[]> => {
    const response = await apiClient.get<Discount[]>('/discounts', { params });
    return response.data;
  },

  createDiscount: async (data: Partial<Discount>): Promise<Discount> => {
    const response = await apiClient.post<Discount>('/discounts', data);
    return response.data;
  },
};

