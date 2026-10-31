# Brightloop 360 Backend Sample

This is a FastAPI and MySQL starter for the Brightloop 360 subscription-management design. It implements the first vertical slice: customers, invoice line snapshots and totals, transactional payment allocation, invoice status updates, and idempotent payment submissions.

## Structure

```
app/
  api/v1/endpoints/     HTTP handlers
  core/                 configuration and database session
  models/               SQLAlchemy 2 domain mappings
  schemas/              Pydantic request and response contracts
  services/             transaction-bound financial rules
```

The model layer also includes products, variants, plans, subscriptions, subscription items, and billing runs so subsequent endpoint modules have a consistent base. Add quotations, taxes, discounts, users/RBAC, audit logs, scheduled billing and Alembic migrations in that order.

## Run locally

1. Create a MySQL 8 database named `brightloop360` and a least-privilege application user.
2. Copy `.env.example` to `.env` and update `DATABASE_URL`.
3. Create an environment and install dependencies:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

4. Open `http://127.0.0.1:8000/docs`.

During local development the app creates tables on startup. Replace that convenience hook with Alembic migrations before shared deployment. Never use `create_all` and an initial Alembic migration as competing schema sources.

## Example workflow

Create a customer:

```json
POST /api/v1/customers/
{"customer_code":"CUST-1001","name":"Asha Rao","email":"asha@example.com"}
```

Create an invoice with snapshots:

```json
POST /api/v1/invoices/
{"customer_id":1,"due_date":"2026-11-15","items":[{"description":"Pro plan November","quantity":1,"unit_price":999,"tax_rate_percent":18}]}
```

Record a payment exactly once (reuse the same idempotency key safely after a network retry):

```json
POST /api/v1/payments/
{"customer_id":1,"amount":1178.82,"payment_method":"upi","idempotency_key":"payment-request-0001","allocations":[{"invoice_id":1,"amount":1178.82}]}
```

## Important implementation notes

- Money uses `Decimal`/`NUMERIC(12,2)`, never floats.
- Invoices preserve customer and line-item snapshots.
- Payment allocation locks invoices, validates customer ownership and prevents over-allocation.
- `billing_runs` has a unique subscription and period constraint to support idempotent recurring billing.
- Successful payments should be refunded/credited through ledger records, not edited or deleted.
