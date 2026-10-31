import { apiClient } from './client';
import {
  Subscription,
  SubscriptionCreateInput,
  SubscriptionStatusTransition,
} from '../types';

export const subscriptionsApi = {
  list: async (params?: { customer_id?: number; plan_id?: number; status?: string }): Promise<Subscription[]> => {
    const response = await apiClient.get<Subscription[]>('/subscriptions', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Subscription> => {
    const response = await apiClient.get<Subscription>(`/subscriptions/${id}`);
    return response.data;
  },

  create: async (data: SubscriptionCreateInput): Promise<Subscription> => {
    const response = await apiClient.post<Subscription>('/subscriptions', data);
    return response.data;
  },

  transitionLifecycle: async (id: number, req: SubscriptionStatusTransition): Promise<Subscription> => {
    const response = await apiClient.post<Subscription>(`/subscriptions/${id}/lifecycle`, req);
    return response.data;
  },

  cancel: async (id: number, reason?: string): Promise<Subscription> => {
    const response = await apiClient.post<Subscription>(`/subscriptions/${id}/cancel`, null, {
      params: { reason },
    });
    return response.data;
  },
};

