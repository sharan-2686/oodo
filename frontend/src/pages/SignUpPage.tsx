import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Zap, Eye, EyeOff, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const customerSchema = z.object({
  full_name: z.string().min(2, 'Full name is required'),
  email: z.string().email('Valid email address required'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  customer_type: z.enum(['individual', 'business']),
  phone: z.string().optional(),
  company_name: z.string().optional(),
  billing_city: z.string().optional(),
  billing_state: z.string().optional(),
  billing_country: z.string().default('IN'),
});

const staffSchema = z.object({
  full_name: z.string().min(2, 'Full name is required'),
  email: z.string().email('Valid email address required'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  role: z.enum(['sales', 'finance', 'support']),
});

type CustomerForm = z.infer<typeof customerSchema>;
type StaffForm = z.infer<typeof staffSchema>;
type SignupTab = 'customer' | 'staff';

const SignUpPage: React.FC = () => {
  const navigate = useNavigate();
  const { signupCustomer, signupStaff } = useAuth();
  const [tab, setTab] = useState<SignupTab>('customer');
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const cForm = useForm<CustomerForm>({
    resolver: zodResolver(customerSchema),
    defaultValues: { customer_type: 'individual', billing_country: 'IN' },
  });

  const sForm = useForm<StaffForm>({
    resolver: zodResolver(staffSchema),
    defaultValues: { role: 'sales' },
  });

  const onCustomerSubmit = async (data: CustomerForm) => {
    setLoading(true);
    setError('');
    try {
      await signupCustomer({
        email: data.email as string,
        password: data.password as string,
        full_name: data.full_name as string,
        customer_type: (data.customer_type ?? 'individual') as 'individual' | 'business',
        phone: data.phone,
        company_name: data.company_name,
        billing_city: data.billing_city,
        billing_state: data.billing_state,
        billing_country: data.billing_country || 'IN',
      });
      navigate('/customer/dashboard');
    } catch (e: any) {
      const msg = e?.response?.data?.detail;
      setError(typeof msg === 'string' ? msg : 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onStaffSubmit = async (data: StaffForm) => {
    setLoading(true);
    setError('');
    try {
      await signupStaff({
        email: data.email as string,
        password: data.password as string,
        full_name: data.full_name as string,
        role: (data.role ?? 'sales') as 'sales' | 'finance' | 'support',
      });
      navigate('/staff/dashboard');
    } catch (e: any) {
      const msg = e?.response?.data?.detail;
      setError(typeof msg === 'string' ? msg : 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const switchTab = (t: SignupTab) => {
    setTab(t);
    setError('');
  };

  return (
    <div className="min-h-screen bg-ivory flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: '#6B1A2A' }}>
              <Zap size={18} style={{ color: '#C9A84C' }} />
            </div>
            <span
              className="font-semibold text-xl text-ink"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
            >
              Brightloop 360
            </span>
          </Link>
          <h1 className="text-2xl font-bold text-ink" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            Create your account
          </h1>
          <p className="text-sm text-muted mt-1">
            Join businesses managing subscriptions smarter
          </p>
        </div>

        <div className="glass-card-strong p-7">
          {/* Tab switcher */}
          <div
            className="flex rounded-lg p-1 mb-6"
            style={{ background: '#F2EDE6', border: '1px solid #E2D9D0' }}
          >
            {(['customer', 'staff'] as SignupTab[]).map((t) => (
              <button
                key={t}
                onClick={() => switchTab(t)}
                className="flex-1 py-2 text-sm font-medium rounded-md transition-all"
                style={
                  tab === t
                    ? { background: '#6B1A2A', color: '#FAF7F2' }
                    : { color: '#7A6860', background: 'transparent' }
                }
              >
                {t === 'customer' ? 'Customer Account' : 'Staff Account'}
              </button>
            ))}
          </div>

          {error && (
            <div
              className="text-sm px-4 py-3 rounded-lg mb-4"
              style={{ background: '#FFE5E5', color: '#8B1A1A', border: '1px solid rgba(139,26,26,0.2)' }}
            >
              {error}
            </div>
          )}

          {/* Customer form */}
          {tab === 'customer' && (
            <form onSubmit={cForm.handleSubmit(onCustomerSubmit)} className="space-y-4">
              <div>
                <label className="form-label">Full Name</label>
                <input {...cForm.register('full_name')} className="form-input" placeholder="John Doe" />
                {cForm.formState.errors.full_name && (
                  <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{cForm.formState.errors.full_name.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Email Address</label>
                <input {...cForm.register('email')} type="email" className="form-input" placeholder="john@company.com" />
                {cForm.formState.errors.email && (
                  <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{cForm.formState.errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Password</label>
                <div className="relative">
                  <input
                    {...cForm.register('password')}
                    type={showPass ? 'text' : 'password'}
                    className="form-input"
                    style={{ paddingRight: '40px' }}
                    placeholder="Minimum 6 characters"
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
                {cForm.formState.errors.password && (
                  <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{cForm.formState.errors.password.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Account Type</label>
                <select {...cForm.register('customer_type')} className="form-input">
                  <option value="individual">Individual</option>
                  <option value="business">Business</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="form-label">Phone</label>
                  <input {...cForm.register('phone')} className="form-input" placeholder="+91 99999 99999" />
                </div>
                <div>
                  <label className="form-label">Company Name</label>
                  <input {...cForm.register('company_name')} className="form-input" placeholder="Optional" />
                </div>
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full py-3 mt-1">
                {loading
                  ? <><Loader2 size={16} className="animate-spin" /> Creating account...</>
                  : 'Create Customer Account'}
              </button>
            </form>
          )}

          {/* Staff form */}
          {tab === 'staff' && (
            <form onSubmit={sForm.handleSubmit(onStaffSubmit)} className="space-y-4">
              <div>
                <label className="form-label">Full Name</label>
                <input {...sForm.register('full_name')} className="form-input" placeholder="Jane Smith" />
                {sForm.formState.errors.full_name && (
                  <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{sForm.formState.errors.full_name.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Work Email</label>
                <input {...sForm.register('email')} type="email" className="form-input" placeholder="jane@brightloop.io" />
                {sForm.formState.errors.email && (
                  <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{sForm.formState.errors.email.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Password</label>
                <div className="relative">
                  <input
                    {...sForm.register('password')}
                    type={showPass ? 'text' : 'password'}
                    className="form-input"
                    style={{ paddingRight: '40px' }}
                    placeholder="Minimum 6 characters"
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
                {sForm.formState.errors.password && (
                  <p className="text-xs mt-1" style={{ color: '#8B1A1A' }}>{sForm.formState.errors.password.message}</p>
                )}
              </div>

              <div>
                <label className="form-label">Department Role</label>
                <select {...sForm.register('role')} className="form-input">
                  <option value="sales">Sales</option>
                  <option value="finance">Finance</option>
                  <option value="support">Support</option>
                </select>
                <p className="text-xs text-muted mt-1">Admin accounts are provisioned by your administrator.</p>
              </div>

              <button type="submit" disabled={loading} className="btn-primary w-full py-3 mt-1">
                {loading
                  ? <><Loader2 size={16} className="animate-spin" /> Creating account...</>
                  : 'Create Staff Account'}
              </button>
            </form>
          )}

          <p className="text-center text-sm text-muted mt-5">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold hover:underline" style={{ color: '#6B1A2A' }}>
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignUpPage;
