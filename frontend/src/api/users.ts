import { apiClient } from './client';
import { User, Role } from '../types';

export interface UserCreateInput {
  email: string;
  password: string;
  full_name: string;
  role_id: number;
}

export const usersApi = {
  list: async (params?: { skip?: number; limit?: number }): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users', { params });
    return response.data;
  },

  create: async (data: UserCreateInput): Promise<User> => {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  },

  listRoles: async (): Promise<Role[]> => {
    const response = await apiClient.get<Role[]>('/users/roles');
    return response.data;
  },

  getById: async (id: number): Promise<User> => {
    const response = await apiClient.get<User>(`/users/${id}`);
    return response.data;
  },
};

