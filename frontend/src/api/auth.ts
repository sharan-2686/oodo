import { apiClient } from './client';
import { TokenResponse, User } from '../types';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface CustomerSignupPayload {
  email: string;
  password: string;
  full_name: string;
  customer_type?: 'individual' | 'business';
  phone?: string;
  company_name?: string;
  tax_identifier?: string;
  billing_address_line1?: string;
  billing_city?: string;
  billing_state?: string;
  billing_postal_code?: string;
  billing_country?: string;
}

export interface StaffSignupPayload {
  email: string;
  password: string;
  full_name: string;
  role?: 'sales' | 'finance' | 'support';
}

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/login', credentials);
    return data;
  },

  signupCustomer: async (payload: CustomerSignupPayload): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/signup/customer', payload);
    return data;
  },

  signupStaff: async (payload: StaffSignupPayload): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/signup/staff', payload);
    return data;
  },

  logout: async (refreshToken?: string): Promise<void> => {
    try {
      if (refreshToken) {
        await apiClient.post('/auth/logout', { refresh_token: refreshToken });
      }
    } catch {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  getCurrentUser: async (): Promise<User> => {
    const { data } = await apiClient.get<User>('/auth/me');
    return data;
  },

  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return data;
  },
};
