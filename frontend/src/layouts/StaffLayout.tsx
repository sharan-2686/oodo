import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, ClipboardList,
  FileText, CreditCard, LogOut, Zap, ChevronRight, Menu, X,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface NavItem {
  icon: React.ElementType;
  label: string;
  path: string;
  permission?: string;
}

const allNavItems: NavItem[] = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/staff/dashboard', permission: 'dashboard:read' },
  { icon: Users, label: 'Customers', path: '/staff/customers', permission: 'customer:read' },
  { icon: ClipboardList, label: 'Quotations', path: '/staff/quotations', permission: 'quotation:read' },
  { icon: FileText, label: 'Subscriptions', path: '/staff/subscriptions', permission: 'subscription:read' },
  { icon: FileText, label: 'Invoices', path: '/staff/invoices', permission: 'invoice:read' },
  { icon: CreditCard, label: 'Payments', path: '/staff/payments', permission: 'payments:read' },
];

const StaffLayout: React.FC = () => {
  const { user, logout, hasPermission } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const roleName = user?.role?.name?.toLowerCase() ?? '';
  const roleLabel = roleName.charAt(0).toUpperCase() + roleName.slice(1);

  const navItems = allNavItems.filter(
    (item) => !item.permission || hasPermission(item.permission)
  );

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Brand */}
      <div
        className="flex items-center gap-2.5 px-5 py-5"
        style={{ borderBottom: '1px solid rgba(184,92,110,0.15)' }}
      >
        <div className="w-7 h-7 rounded-lg flex items-center justify-center"
          style={{ background: 'rgba(201,168,76,0.2)' }}>
          <Zap size={14} style={{ color: '#C9A84C' }} />
        </div>
        <div>
          <p className="text-white text-xs font-semibold" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            Brightloop 360
          </p>
          <p className="text-xs" style={{ color: 'rgba(250,247,242,0.4)' }}>{roleLabel} Portal</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map((item) => {
          const active = location.pathname === item.path ||
            (item.path !== '/staff/dashboard' && location.pathname.startsWith(item.path));
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all"
              style={
                active
                  ? { background: 'rgba(201,168,76,0.18)', color: '#C9A84C', fontWeight: 500 }
                  : { color: 'rgba(250,247,242,0.65)' }
              }
            >
              <item.icon size={15} />
              {item.label}
              {active && <ChevronRight size={12} className="ml-auto" style={{ color: '#C9A84C' }} />}
            </Link>
          );
        })}
      </nav>

      {/* User Footer */}
      <div className="px-4 py-4" style={{ borderTop: '1px solid rgba(184,92,110,0.15)' }}>
        <div className="flex items-center gap-2.5 mb-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0"
            style={{ background: 'rgba(201,168,76,0.2)', color: '#C9A84C' }}
          >
            {user?.full_name?.[0]?.toUpperCase() ?? 'S'}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-white truncate">{user?.full_name}</p>
            <p className="text-xs truncate" style={{ color: 'rgba(250,247,242,0.4)' }}>{roleLabel}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs transition-all"
          style={{ color: 'rgba(250,247,242,0.5)' }}
        >
          <LogOut size={13} />
          Sign Out
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-ivory flex">
      {/* Desktop sidebar — 20% width */}
      <aside
        className="hidden lg:flex flex-col flex-shrink-0"
        style={{
          width: '20%',
          minWidth: '200px',
          maxWidth: '240px',
          background: '#6B1A2A',
          borderRight: '1px solid rgba(184,92,110,0.2)',
          boxShadow: '4px 0 24px rgba(28,20,16,0.12)',
          position: 'sticky',
          top: 0,
          height: '100vh',
          overflowY: 'auto',
        }}
      >
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div
            className="fixed inset-0"
            style={{ background: 'rgba(28,20,16,0.5)' }}
            onClick={() => setSidebarOpen(false)}
          />
          <aside
            className="relative flex flex-col"
            style={{
              width: '240px',
              background: '#6B1A2A',
              zIndex: 51,
              height: '100vh',
              overflowY: 'auto',
            }}
          >
            <button
              onClick={() => setSidebarOpen(false)}
              className="absolute top-4 right-4 text-white/60 hover:text-white"
            >
              <X size={18} />
            </button>
            <SidebarContent />
          </aside>
        </div>
      )}

      {/* Main area — 80% */}
      <div className="flex-1 flex flex-col min-w-0" style={{ width: '80%' }}>
        {/* Mobile top bar */}
        <div className="lg:hidden navbar-glass flex items-center justify-between px-4 py-3">
          <button onClick={() => setSidebarOpen(true)}>
            <Menu size={20} style={{ color: '#6B1A2A' }} />
          </button>
          <span className="text-sm font-semibold text-ink">Brightloop 360</span>
          <div />
        </div>

        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default StaffLayout;
