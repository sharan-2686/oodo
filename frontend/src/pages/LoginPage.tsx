import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Zap, Eye, EyeOff, Loader2, LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const schema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type FormData = z.infer<typeof schema>;

const demoAccounts = [
  { label: 'Admin', email: 'admin@brightloop.io', password: 'Admin@12345' },
  { label: 'Sales', email: 'sales@brightloop.io', password: 'Sales@12345' },
  { label: 'Finance', email: 'finance@brightloop.io', password: 'Finance@12345' },
  { label: 'Support', email: 'support@brightloop.io', password: 'Support@12345' },
];

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register, handleSubmit, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    setError('');
    try {
      const response = await login({ email: data.email as string, password: data.password as string });
      const role = response.user?.role?.name?.toLowerCase() ?? '';
      if (role === 'admin') navigate('/admin/dashboard');
      else if (['sales', 'finance', 'support'].includes(role)) navigate('/staff/dashboard');
      else navigate('/customer/dashboard');
    } catch (e: any) {
      const msg = e?.response?.data?.detail;
      setError(typeof msg === 'string' ? msg : 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (acc: typeof demoAccounts[number]) => {
    setValue('email', acc.email);
    setValue('password', acc.password);
  };

  return (
    <div className="min-h-screen bg-ivory flex">
      {/* Left decorative panel */}
      <div
        className="hidden lg:flex lg:w-5/12 flex-col justify-between p-12"
        style={{ background: '#6B1A2A' }}
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'rgba(255,255,255,0.1)' }}>
            <Zap size={18} style={{ color: '#C9A84C' }} />
          </div>
          <span
            className="font-semibold text-xl text-white"
            style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
          >
            Brightloop 360
          </span>
        </div>

        <div>
          <h2
            className="text-4xl font-bold text-white leading-tight mb-5"
            style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
          >
            Your complete revenue operations platform
          </h2>
          <p className="text-sm leading-relaxed mb-8" style={{ color: 'rgba(250,247,242,0.6)' }}>
            Manage subscriptions, automate billing, track payments, and grow your business — all from a single unified dashboard.
          </p>
          <div className="space-y-3">
            {[
              'Automated subscription billing',
              'Real-time revenue analytics',
              'Integrated Razorpay payments',
              'Role-based team access controls',
            ].map((item) => (
              <div key={item} className="flex items-center gap-3">
                <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ background: 'rgba(201,168,76,0.2)' }}>
                  <div className="w-2 h-2 rounded-full" style={{ background: '#C9A84C' }} />
                </div>
                <span className="text-sm" style={{ color: 'rgba(250,247,242,0.8)' }}>{item}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs" style={{ color: 'rgba(250,247,242,0.25)' }}>
          Brightloop 360 — Hackathon 2026
        </p>
      </div>

      {/* Right form panel */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          {/* Mobile brand */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: '#6B1A2A' }}>
              <Zap size={16} style={{ color: '#C9A84C' }} />
            </div>
            <span className="font-semibold text-lg text-ink"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
              Brightloop 360
            </span>
          </div>

          <div className="mb-8">
            <h1 className="text-2xl font-bold text-ink mb-1"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
              Welcome back
            </h1>
            <p className="text-sm text-muted">Sign in to access your dashboard</p>
          </div>

          <div className="glass-card-strong p-6">
            {error && (
              <div
                className="text-sm px-4 py-3 rounded-lg mb-4"
                style={{ background: '#FFE5E5', color: '#8B1A1A', border: '1px solid rgba(139,26,26,0.2)' }}
              >
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <label className="form-label">Email Address</label>
                <input
                  {...register('email')}
                  type="email"
                  className="form-input"
                  placeholder="you@company.com"
                  autoComplete="email"
                />
                {errors.email && <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{errors.email.message}</p>}
              </div>

              <div>
                <label className="form-label">Password</label>
                <div className="relative">
                  <input
                    {...register('password')}
                    type={showPass ? 'text' : 'password'}
                    className="form-input"
                    style={{ paddingRight: '40px' }}
                    placeholder="Your password"
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass(!showPass)}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                    style={{ color: '#7A6860' }}
                  >
                    {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.password && <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{errors.password.message}</p>}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full py-3 mt-1"
              >
                {loading
                  ? <><Loader2 size={16} className="animate-spin" /> Signing in...</>
                  : <><LogIn size={16} /> Sign In</>}
              </button>
            </form>

            {/* Demo accounts */}
            <div className="mt-5 pt-4" style={{ borderTop: '1px solid #E2D9D0' }}>
              <p className="text-xs text-center text-muted mb-3">Quick Demo Access</p>
              <div className="grid grid-cols-2 gap-2">
                {demoAccounts.map((acc) => (
                  <button
                    key={acc.label}
                    type="button"
                    onClick={() => fillDemo(acc)}
                    className="text-left text-xs py-2 px-3 rounded-lg transition-all"
                    style={{
                      background: '#F2EDE6',
                      border: '1px solid #E2D9D0',
                      color: '#7A6860',
                    }}
                    onMouseEnter={(e) => {
                      (e.currentTarget as HTMLElement).style.borderColor = 'rgba(107,26,42,0.3)';
                      (e.currentTarget as HTMLElement).style.color = '#1C1410';
                    }}
                    onMouseLeave={(e) => {
                      (e.currentTarget as HTMLElement).style.borderColor = '#E2D9D0';
                      (e.currentTarget as HTMLElement).style.color = '#7A6860';
                    }}
                  >
                    <span className="font-semibold text-ink block">{acc.label}</span>
                    <span className="opacity-60 text-xs">{acc.email}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <p className="text-center text-sm text-muted mt-6">
            New to Brightloop 360?{' '}
            <Link to="/signup" className="font-semibold hover:underline" style={{ color: '#6B1A2A' }}>
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
