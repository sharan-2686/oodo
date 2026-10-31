import React from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart2, CheckCircle, Users, FileText, CreditCard,
  TrendingUp, Shield, Zap, Star, ArrowRight,
} from 'lucide-react';

const features = [
  {
    icon: Users,
    title: 'Customer Management',
    desc: 'Centralize customer profiles, billing data, and communication history in one unified workspace.',
  },
  {
    icon: FileText,
    title: 'Quotation Engine',
    desc: 'Generate professional quotes, apply discounts and taxes, and convert to subscriptions instantly.',
  },
  {
    icon: BarChart2,
    title: 'Revenue Analytics',
    desc: 'Track MRR, ARR, churn, and payment trends with real-time insights and visual dashboards.',
  },
  {
    icon: CreditCard,
    title: 'Integrated Payments',
    desc: 'Accept payments via Razorpay with automatic reconciliation and invoice allocation.',
  },
  {
    icon: TrendingUp,
    title: 'Subscription Lifecycle',
    desc: 'Manage trials, activations, renewals, pauses, and cancellations end to end.',
  },
  {
    icon: Shield,
    title: 'Role-Based Access',
    desc: 'Granular permissions for Admin, Sales, Finance, and Support teams out of the box.',
  },
];

const plans = [
  {
    name: 'Starter',
    price: '999',
    features: ['Up to 100 customers', 'Quotation management', 'Basic reporting', 'Email support'],
    highlight: false,
  },
  {
    name: 'Professional',
    price: '2,499',
    features: ['Up to 1,000 customers', 'Advanced analytics', 'Razorpay integration', 'Priority support', 'Custom branding'],
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    features: ['Unlimited customers', 'Dedicated account manager', 'Custom integrations', 'SLA guarantee', 'On-premise option'],
    highlight: false,
  },
];

const steps = [
  { num: '01', title: 'Create Quote', desc: 'Build itemized quotes with products, plans, taxes and discounts.' },
  { num: '02', title: 'Get Accepted', desc: 'Customer reviews and accepts the quote via the self-service portal.' },
  { num: '03', title: 'Auto-Subscribe', desc: 'Subscription activates automatically with invoice generation.' },
  { num: '04', title: 'Collect Payment', desc: 'Razorpay integration handles payment and auto-reconciliation.' },
];

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-ivory font-sans">
      {/* Sticky Navigation */}
      <nav className="navbar-glass sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Zap size={16} className="text-gold" />
            </div>
            <span
              className="font-semibold text-lg text-ink"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
            >
              Brightloop 360
            </span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-muted hover:text-ink transition-colors">Features</a>
            <a href="#workflow" className="text-sm text-muted hover:text-ink transition-colors">How it Works</a>
            <a href="#pricing" className="text-sm text-muted hover:text-ink transition-colors">Pricing</a>
          </div>

          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary text-sm px-4 py-2">Sign In</Link>
            <Link to="/signup" className="btn-primary text-sm px-4 py-2">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden pt-20 pb-28">
        <div
          className="absolute inset-0 pointer-events-none"
          style={{
            background:
              'radial-gradient(ellipse 800px 500px at 50% -100px, rgba(107,26,42,0.06) 0%, transparent 70%), radial-gradient(ellipse 400px 400px at 90% 80%, rgba(201,168,76,0.05) 0%, transparent 60%)',
          }}
        />

        <div className="relative max-w-5xl mx-auto px-6 text-center">
          <div className="inline-flex items-center gap-2 bg-primary/8 border border-primary/15 text-primary text-xs font-semibold px-4 py-1.5 rounded-full mb-8"
            style={{ background: 'rgba(107,26,42,0.07)' }}>
            <Star size={12} />
            Enterprise Subscription Management Platform
          </div>

          <h1
            className="text-5xl md:text-6xl font-bold text-ink leading-tight mb-6"
            style={{ fontFamily: '"Playfair Display", Georgia, serif', textWrap: 'balance' }}
          >
            Revenue Operations,{' '}
            <span style={{ color: '#6B1A2A' }}>Fully Automated</span>
          </h1>

          <p className="text-lg text-muted max-w-2xl mx-auto mb-10 leading-relaxed">
            Brightloop 360 unifies your subscription billing, customer management, quotations,
            and payment collection in a single intelligent platform built for growth.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link to="/signup" className="btn-primary px-8 py-3 text-base">
              Start Free Trial <ArrowRight size={16} />
            </Link>
            <Link to="/login" className="btn-secondary px-8 py-3 text-base">
              Sign In to Dashboard
            </Link>
          </div>
          <p className="text-xs text-muted mt-4">No credit card required. 14-day free trial.</p>

          {/* Stats strip */}
          <div className="mt-16 grid grid-cols-3 gap-4 max-w-lg mx-auto">
            {[['99.9%', 'Uptime SLA'], ['INR', 'Native Currency'], ['14-Day', 'Free Trial']].map(([val, lbl]) => (
              <div key={lbl} className="glass-card p-4 text-center">
                <div className="font-semibold text-xl text-primary mb-0.5"
                  style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>{val}</div>
                <div className="text-xs text-muted">{lbl}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24" style={{ background: '#F2EDE6' }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2
              className="text-3xl font-bold text-ink mb-3"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
            >
              Everything you need to run subscriptions
            </h2>
            <p className="text-muted max-w-xl mx-auto text-sm leading-relaxed">
              A complete platform that handles every touchpoint of your subscription business — from first quote to final payment.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f) => (
              <div key={f.title} className="glass-card p-6 hover:shadow-glass-lg transition-all duration-300 group">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center mb-4 transition-colors"
                  style={{ background: 'rgba(107,26,42,0.1)' }}
                >
                  <f.icon size={20} style={{ color: '#6B1A2A' }} />
                </div>
                <h3 className="font-semibold text-ink mb-2 text-sm">{f.title}</h3>
                <p className="text-xs text-muted leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="workflow" className="py-24 bg-ivory">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2
              className="text-3xl font-bold text-ink mb-3"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
            >
              From quote to cash, in minutes
            </h2>
            <p className="text-muted text-sm">A seamless end-to-end workflow for every subscription deal.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {steps.map((s, i) => (
              <div key={s.num} className="relative">
                <div className="glass-card p-5 text-center h-full">
                  <div
                    className="text-3xl font-bold mb-2"
                    style={{ fontFamily: '"Playfair Display", Georgia, serif', color: 'rgba(107,26,42,0.18)' }}
                  >
                    {s.num}
                  </div>
                  <h4 className="font-semibold text-ink text-sm mb-2">{s.title}</h4>
                  <p className="text-xs text-muted leading-relaxed">{s.desc}</p>
                </div>
                {i < 3 && (
                  <div className="hidden md:block absolute top-1/2 -right-2.5 z-10">
                    <ArrowRight size={14} style={{ color: '#E2D9D0' }} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24" style={{ background: '#F2EDE6' }}>
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center mb-14">
            <h2
              className="text-3xl font-bold text-ink mb-3"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
            >
              Simple, transparent pricing
            </h2>
            <p className="text-muted text-sm">All plans include a 14-day free trial. No setup fees.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((p) => (
              <div
                key={p.name}
                className="rounded-xl p-6 flex flex-col"
                style={
                  p.highlight
                    ? { background: '#6B1A2A', boxShadow: '0 0 30px rgba(107,26,42,0.25)' }
                    : { background: 'rgba(242,237,230,0.85)', border: '1px solid #E2D9D0', backdropFilter: 'blur(16px)' }
                }
              >
                {p.highlight && (
                  <div className="text-xs font-semibold px-3 py-1 rounded-full self-start mb-4 text-ink"
                    style={{ background: '#C9A84C' }}>
                    Most Popular
                  </div>
                )}
                <h3
                  className="text-xl font-bold mb-1"
                  style={{
                    fontFamily: '"Playfair Display", Georgia, serif',
                    color: p.highlight ? '#FAF7F2' : '#1C1410',
                  }}
                >
                  {p.name}
                </h3>
                <div className="mb-6">
                  <span
                    className="text-3xl font-bold"
                    style={{ color: p.highlight ? '#FAF7F2' : '#1C1410', fontFamily: '"Playfair Display", Georgia, serif' }}
                  >
                    {p.price === 'Custom' ? 'Custom' : `₹${p.price}`}
                  </span>
                  {p.price !== 'Custom' && (
                    <span className="text-sm" style={{ color: p.highlight ? 'rgba(250,247,242,0.6)' : '#7A6860' }}>/month</span>
                  )}
                </div>
                <ul className="space-y-3 flex-1 mb-6">
                  {p.features.map((f) => (
                    <li key={f} className="flex items-center gap-2 text-sm">
                      <CheckCircle size={14} style={{ color: p.highlight ? '#C9A84C' : '#6B1A2A', flexShrink: 0 }} />
                      <span style={{ color: p.highlight ? 'rgba(250,247,242,0.9)' : '#1C1410' }}>{f}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  to="/signup"
                  className="text-center py-2.5 rounded-lg text-sm font-medium transition-all block"
                  style={
                    p.highlight
                      ? { background: '#C9A84C', color: '#1C1410' }
                      : { background: '#6B1A2A', color: '#FAF7F2' }
                  }
                >
                  Get Started
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-20" style={{ background: '#6B1A2A' }}>
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2
            className="text-3xl font-bold text-white mb-4"
            style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
          >
            Ready to transform your revenue operations?
          </h2>
          <p className="mb-8 text-sm leading-relaxed" style={{ color: 'rgba(250,247,242,0.65)' }}>
            Join growing businesses using Brightloop 360 to automate billing and maximize revenue.
          </p>
          <Link to="/signup" className="btn-gold px-10 py-3 text-base">
            Start Your Free Trial <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ background: '#1C1410' }} className="py-10">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-md flex items-center justify-center" style={{ background: '#6B1A2A' }}>
              <Zap size={12} style={{ color: '#C9A84C' }} />
            </div>
            <span
              className="text-white text-sm font-semibold"
              style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
            >
              Brightloop 360
            </span>
          </div>
          <p className="text-xs" style={{ color: '#7A6860' }}>
            © 2026 Brightloop 360. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

