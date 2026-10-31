import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/common/ProtectedRoute';

// Layouts
import AdminLayout from './layouts/AdminLayout';
import StaffLayout from './layouts/StaffLayout';
import CustomerLayout from './layouts/CustomerLayout';

// Public pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignUpPage from './pages/SignUpPage';

// Admin pages
import AdminDashboard from './pages/admin/AdminDashboard';
import UsersPage from './pages/admin/UsersPage';

// Staff pages
import StaffDashboard from './pages/staff/StaffDashboard';

// Customer pages
import CustomerCatalog from './pages/customer/CustomerCatalog';
import CustomerInvoices from './pages/customer/CustomerInvoices';
import CustomerQuotations from './pages/customer/CustomerQuotations';
import CustomerSubscriptions from './pages/customer/CustomerSubscriptions';

// Existing staff pages (reused)
import { CustomersPage } from './pages/CustomersPage';
import { ProductsPage } from './pages/ProductsPage';
import { PlansPage } from './pages/PlansPage';
import { QuotationsPage } from './pages/QuotationsPage';
import { SubscriptionsPage } from './pages/SubscriptionsPage';
import { InvoicesPage } from './pages/InvoicesPage';
import { PaymentsPage } from './pages/PaymentsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

// Smart redirect after login based on role
const RoleRedirect: React.FC = () => {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;

  const role = user?.role?.name?.toLowerCase() ?? '';
  if (role === 'admin') return <Navigate to="/admin/dashboard" replace />;
  if (['sales', 'finance', 'support'].includes(role)) return <Navigate to="/staff/dashboard" replace />;
  if (role === 'customer') return <Navigate to="/customer/catalog" replace />;
  return <Navigate to="/login" replace />;
};

// Guard that only allows a specific role
const RoleGuard: React.FC<{ role: string | string[] }> = ({ role }) => {
  const { user, isLoading, isAuthenticated } = useAuth();

  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;

  const userRole = user?.role?.name?.toLowerCase() ?? '';
  const allowed = Array.isArray(role) ? role.includes(userRole) : userRole === role;
  if (!allowed) return <RoleRedirect />;
  return <Outlet />;
};

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignUpPage />} />

      {/* Admin routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<RoleGuard role="admin" />}>
          <Route element={<AdminLayout />}>
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            <Route path="/admin/customers" element={<CustomersPage />} />
            <Route path="/admin/products" element={<ProductsPage />} />
            <Route path="/admin/plans" element={<PlansPage />} />
            <Route path="/admin/quotations" element={<QuotationsPage />} />
            <Route path="/admin/subscriptions" element={<SubscriptionsPage />} />
            <Route path="/admin/invoices" element={<InvoicesPage />} />
            <Route path="/admin/payments" element={<PaymentsPage />} />
            <Route path="/admin/users" element={<UsersPage />} />
          </Route>
        </Route>
      </Route>

      {/* Staff routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<RoleGuard role={['sales', 'finance', 'support']} />}>
          <Route element={<StaffLayout />}>
            <Route path="/staff/dashboard" element={<StaffDashboard />} />
            <Route path="/staff/customers" element={<CustomersPage />} />
            <Route path="/staff/quotations" element={<QuotationsPage />} />
            <Route path="/staff/subscriptions" element={<SubscriptionsPage />} />
            <Route path="/staff/invoices" element={<InvoicesPage />} />
            <Route path="/staff/payments" element={<PaymentsPage />} />
          </Route>
        </Route>
      </Route>

      {/* Customer routes */}
      <Route element={<ProtectedRoute />}>
        <Route element={<RoleGuard role="customer" />}>
          <Route element={<CustomerLayout />}>
            <Route path="/customer/dashboard" element={<Navigate to="/customer/catalog" replace />} />
            <Route path="/customer/catalog" element={<CustomerCatalog />} />
            <Route path="/customer/invoices" element={<CustomerInvoices />} />
            <Route path="/customer/quotations" element={<CustomerQuotations />} />
            <Route path="/customer/subscriptions" element={<CustomerSubscriptions />} />
            <Route path="/customer/profile" element={<div className="page-container"><p className="text-muted">Profile management coming soon.</p></div>} />
          </Route>
        </Route>
      </Route>

      {/* Smart redirect for authenticated users */}
      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<RoleRedirect />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <AppRoutes />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
