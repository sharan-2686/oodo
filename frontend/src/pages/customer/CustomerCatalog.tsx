import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { ShoppingBag, Search, Package, Loader2, FileText } from 'lucide-react';
import { catalogApi } from '../../api/catalog';
import { quotationsApi } from '../../api/quotations';
import { Product, QuotationCreateInput } from '../../types';

const formatCurrency = (val: number | string): string => {
  const num = parseFloat(String(val));
  if (isNaN(num)) return '₹0';
  return `₹${num.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })}`;
};

const CustomerCatalog: React.FC = () => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');

  const { data: products = [], isLoading } = useQuery<Product[]>({
    queryKey: ['customer-products', search, category],
    queryFn: () => catalogApi.listProducts({ category: category || undefined }),
  });

  const quoteMutation = useMutation({
    mutationFn: (data: QuotationCreateInput) => quotationsApi.create(data),
    onSuccess: (quote) => {
      alert(`Quote ${quote.quote_number} generated successfully!`);
      navigate('/customer/quotations');
    },
    onError: (err: any) => {
      const detail = err.response?.data?.detail;
      const msg = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ')
        : 'Failed to request quote';
      alert(msg);
    },
  });

  const categories = [...new Set(products.map((p) => p.category).filter(Boolean))] as string[];

  const filtered = products.filter((p) => p.is_active);

  return (
    <div className="page-container animate-fade-in">
      <div className="section-header mb-6">
        <div className="flex items-center gap-2">
          <ShoppingBag size={20} style={{ color: '#6B1A2A' }} />
          <h1 className="section-title" style={{ fontFamily: '"Playfair Display", Georgia, serif' }}>
            Product Catalog
          </h1>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-6">
        <div className="relative flex-1 min-w-48">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: '#7A6860' }} />
          <input
            type="text"
            className="form-input"
            style={{ paddingLeft: '36px' }}
            placeholder="Search products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        {categories.length > 0 && (
          <select
            className="form-input w-auto"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        )}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-24">
          <Loader2 size={28} className="animate-spin" style={{ color: '#6B1A2A' }} />
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <Package size={40} className="mx-auto mb-3" style={{ color: '#E2D9D0' }} />
          <p className="text-ink font-medium mb-1">No products available</p>
          <p className="text-sm text-muted">Check back later for new products.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((product) => (
            <div key={product.id} className="glass-card overflow-hidden hover:shadow-glass-lg transition-all duration-300">
              {/* Product header */}
              <div className="p-5" style={{ borderBottom: '1px solid #E2D9D0' }}>
                <div className="flex items-start justify-between mb-2">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                    style={{ background: 'rgba(107,26,42,0.08)' }}
                  >
                    <Package size={18} style={{ color: '#6B1A2A' }} />
                  </div>
                  {product.category && (
                    <span className="badge badge-info text-xs">{product.category}</span>
                  )}
                </div>
                <h3 className="font-semibold text-ink mt-3">{product.name}</h3>
                <p className="text-xs text-muted mt-1 leading-relaxed">
                  {product.description || 'No description available.'}
                </p>
              </div>

              {/* Variants */}
              {product.variants && product.variants.length > 0 ? (
                <div className="p-4">
                  <p className="text-xs font-semibold text-muted uppercase mb-3" style={{ letterSpacing: '0.06em' }}>
                    Available Options
                  </p>
                  <div className="space-y-2">
                    {product.variants.filter((v) => v.is_active).map((variant) => (
                      <div
                        key={variant.id}
                        className="p-3 rounded-lg flex flex-col gap-2"
                        style={{ background: '#FAF7F2', border: '1px solid #E2D9D0' }}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm font-medium text-ink">{variant.name}</p>
                            <p className="text-xs text-muted">{variant.sku}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-semibold text-primary text-sm">
                              {formatCurrency(variant.unit_price)}
                            </p>
                            <p className="text-xs text-muted">{variant.currency || 'INR'}</p>
                          </div>
                        </div>
                        <button
                          type="button"
                          disabled={quoteMutation.isPending}
                          onClick={() => {
                            quoteMutation.mutate({
                              currency: variant.currency || 'INR',
                              terms: 'Payment due within 15 days upon acceptance.',
                              items: [
                                {
                                  product_id: product.id,
                                  variant_id: variant.id,
                                  description: `${product.name} (${variant.name})`,
                                  quantity: 1,
                                  unit_price: Number(variant.unit_price) || 0,
                                  tax_rate_percent: 18,
                                },
                              ],
                            });
                          }}
                          className="w-full py-1.5 px-3 rounded-lg bg-[#6B1A2A] text-white text-xs font-semibold hover:bg-[#521320] transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                        >
                          <FileText size={12} />
                          Request Quotation
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="p-4">
                  <p className="text-xs text-muted italic">No variants available</p>
                </div>
              )}

              <div className="px-4 pb-4">
                <p className="text-xs text-muted">
                  To purchase, contact our sales team or request a quote.
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CustomerCatalog;
