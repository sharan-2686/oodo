import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, Package, ClipboardList,
  FileText, CreditCard, Settings, LogOut, Zap,
  BarChart2, ChevronRight,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/admin/dashboard' },
  { icon: Users, label: 'Customers', path: '/admin/customers' },
  { icon: Package, label: 'Products', path: '/admin/products' },
  { icon: BarChart2, label: 'Plans', path: '/admin/plans' },
  { icon: ClipboardList, label: 'Quotations', path: '/admin/quotations' },
  { icon: FileText, label: 'Subscriptions', path: '/admin/subscriptions' },
  { icon: FileText, label: 'Invoices', path: '/admin/invoices' },
  { icon: CreditCard, label: 'Payments', path: '/admin/payments' },
  { icon: Users, label: 'Users', path: '/admin/users' },
];

const AdminLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-ivory flex">
      {/* Sidebar */}
      <aside
        className="w-56 flex-shrink-0 flex flex-col"
        style={{
          background: '#6B1A2A',
          borderRight: '1px solid rgba(184,92,110,0.2)',
          boxShadow: '4px 0 24px rgba(28,20,16,0.12)',
          position: 'sticky',
          top: 0,
          height: '100vh',
          overflowY: 'auto',
        }}
      >
        {/* Brand */}
        <div
          className="flex items-center gap-2.5 px-5 py-5"
          style={{ borderBottom: '1px solid rgba(184,92,110,0.15)' }}
        >
          <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: 'rgba(201,168,76,0.2)' }}>
            <Zap size={14} style={{ color: '#C9A84C' }} />
          </div>
          <div>
            <p className="text-white text-xs font-semibold leading-tight"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
              Brightloop 360
            </p>
            <p className="text-xs" style={{ color: 'rgba(250,247,242,0.4)' }}>Administration</p>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {navItems.map((item) => {
            const active = location.pathname === item.path ||
              (item.path !== '/admin/dashboard' && location.pathname.startsWith(item.path));
            return (
              <Link
                key={item.path}
                to={item.path}
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
        <div
          className="px-4 py-4"
          style={{ borderTop: '1px solid rgba(184,92,110,0.15)' }}
        >
          <div className="flex items-center gap-2.5 mb-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold flex-shrink-0"
              style={{ background: 'rgba(201,168,76,0.2)', color: '#C9A84C' }}
            >
              {user?.full_name?.[0]?.toUpperCase() ?? 'A'}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-white truncate">{user?.full_name}</p>
              <p className="text-xs truncate" style={{ color: 'rgba(250,247,242,0.4)' }}>Administrator</p>
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
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
