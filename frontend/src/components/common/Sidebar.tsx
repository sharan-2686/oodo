import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import {
  LayoutDashboard,
  Users,
  Package,
  Layers,
  FileText,
  Repeat,
  Receipt,
  CreditCard,
  LogOut,
  Zap,
} from 'lucide-react';
import { Badge } from '../ui/Badge';

export const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();

  const navItems = [
    { label: 'Executive Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Customer 360', path: '/customers', icon: Users },
    { label: 'Product Catalog', path: '/products', icon: Package },
    { label: 'Recurring Plans', path: '/plans', icon: Layers },
    { label: 'Quotations', path: '/quotations', icon: FileText },
    { label: 'Subscriptions', path: '/subscriptions', icon: Repeat },
    { label: 'Invoices & Billing', path: '/invoices', icon: Receipt },
    { label: 'Payments & Ledger', path: '/payments', icon: CreditCard },
  ];

  return (
    <aside className="w-64 h-screen sticky top-0 bg-[#070a13]/90 backdrop-blur-2xl border-r border-white/10 flex flex-col justify-between z-30 select-none">
      {/* Brand Header */}
      <div>
        <div className="p-6 pb-4 flex items-center gap-3 border-b border-white/5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-glow-cyan">
            <Zap className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-base tracking-tight text-white">BRIGHTLOOP</span>
              <span className="text-xs font-bold px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                360
              </span>
            </div>
            <p className="text-[10px] uppercase tracking-wider text-slate-400">Subscription & Revenue OS</p>
          </div>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-1 mt-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 group relative ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-white/[0.04]'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      className={`w-4 h-4 transition-colors ${
                        isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'
                      }`}
                    />
                    <span>{item.label}</span>
                    {isActive && (
                      <span className="absolute right-2 w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-glow-cyan" />
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* User Footer & Logout */}
      <div className="p-4 border-t border-white/10 bg-slate-900/40">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-indigo-600/30 border border-indigo-500/30 flex items-center justify-center text-xs font-bold text-indigo-300 shrink-0">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.full_name}</p>
              <Badge variant="cyan" className="text-[9px] px-1.5 py-0 mt-0.5">
                {user?.role?.name || 'Staff'}
              </Badge>
            </div>
          </div>
          <button
            onClick={() => logout()}
            title="Sign out"
            className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
        <div className="text-[10px] text-slate-500 text-center font-mono">
          API v1.0 • Connected
        </div>
      </div>
    </aside>
  );
};

