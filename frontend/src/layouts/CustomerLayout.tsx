import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { ShoppingBag, FileText, CreditCard, User, Zap, LogOut, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { icon: ShoppingBag, label: 'Product Catalog', path: '/customer/catalog' },
  { icon: FileText, label: 'My Quotes', path: '/customer/quotations' },
  { icon: FileText, label: 'My Subscriptions', path: '/customer/subscriptions' },
  { icon: CreditCard, label: 'My Invoices', path: '/customer/invoices' },
  { icon: User, label: 'My Profile', path: '/customer/profile' },
];

const CustomerLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-ivory">
      {/* Top navbar */}
      <nav className="navbar-glass sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: '#6B1A2A' }}>
              <Zap size={15} style={{ color: '#C9A84C' }} />
            </div>
            <span className="font-semibold text-ink text-sm"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
              Brightloop 360
            </span>
          </div>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const active = location.pathname === item.path || location.pathname.startsWith(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm transition-all"
                  style={
                    active
                      ? { background: 'rgba(107,26,42,0.1)', color: '#6B1A2A', fontWeight: 500 }
                      : { color: '#7A6860' }
                  }
                >
                  <item.icon size={14} />
                  {item.label}
                </Link>
              );
            })}
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold"
                style={{ background: 'rgba(107,26,42,0.1)', color: '#6B1A2A' }}
              >
                {user?.full_name?.[0]?.toUpperCase() ?? 'C'}
              </div>
              <span className="text-sm font-medium text-ink hidden sm:block">{user?.full_name}</span>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs text-muted hover:text-ink transition-colors px-2 py-1.5"
            >
              <LogOut size={14} />
              <span className="hidden sm:block">Sign Out</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main>
        <Outlet />
      </main>
    </div>
  );
};

export default CustomerLayout;
