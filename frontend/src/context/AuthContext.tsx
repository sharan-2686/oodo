import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, TokenResponse } from '../types';
import { authApi, CustomerSignupPayload, StaffSignupPayload } from '../api/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: { email: string; password: string }) => Promise<TokenResponse>;
  logout: () => Promise<void>;
  signupCustomer: (payload: CustomerSignupPayload) => Promise<void>;
  signupStaff: (payload: StaffSignupPayload) => Promise<void>;
  hasPermission: (permissionCode: string) => boolean;
  hasRole: (roleName: string) => boolean;
  getRoleName: () => string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        try {
          const profile = await authApi.getCurrentUser();
          setUser(profile);
          localStorage.setItem('user', JSON.stringify(profile));
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          setUser(null);
          setToken(null);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (credentials: { email: string; password: string }): Promise<TokenResponse> => {
    const data = await authApi.login(credentials);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem('refresh_token') || undefined;
    await authApi.logout(refreshToken);
    setToken(null);
    setUser(null);
  };

  const signupCustomer = async (payload: CustomerSignupPayload): Promise<void> => {
    const data = await authApi.signupCustomer(payload);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
  };

  const signupStaff = async (payload: StaffSignupPayload): Promise<void> => {
    const data = await authApi.signupStaff(payload);
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    setToken(data.access_token);
    setUser(data.user);
  };

  const hasPermission = (permissionCode: string): boolean => {
    if (!user) return false;
    if (user.role?.name?.toLowerCase() === 'admin') return true;
    return user.permissions?.includes(permissionCode) ?? false;
  };

  const hasRole = (roleName: string): boolean => {
    if (!user) return false;
    return user.role?.name?.toLowerCase() === roleName.toLowerCase();
  };

  const getRoleName = (): string => {
    return user?.role?.name?.toLowerCase() ?? '';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
        signupCustomer,
        signupStaff,
        hasPermission,
        hasRole,
        getRoleName,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
