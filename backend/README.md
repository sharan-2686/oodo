# Brightloop 360 — Backend & Database Foundation

Welcome to the backend foundation for **Brightloop 360** (FastAPI + MySQL 8 + SQLAlchemy 2 + Alembic).

---

## 1. Architecture Overview

- **Web Framework**: FastAPI (modular monolith)
- **Database Engine**: MySQL 8+ (InnoDB, `utf8mb4`)
- **ORM**: SQLAlchemy 2.0 (mapped columns, strict typing, relationship cascades)
- **Migrations**: Alembic (single source of truth for database schema)
- **Authentication**: JWT Bearer tokens + Argon2id password hashing via `pwdlib` + SHA-256 hashed refresh tokens
- **Access Control**: Role-Based Access Control (RBAC) with granular permission dependencies

---

## 2. Environment Variables (.env)

Create `.env` in the `backend/` folder (or copy from `.env.example`):

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `APP_NAME` | Name of the service | `Brightloop 360` |
| `ENVIRONMENT` | Runtime environment (`development`, `production`, `testing`) | `development` |
| `DEBUG` | Enable debug mode and verbose tracebacks | `True` |
| `SECRET_KEY` | Cryptographic secret for signing JWT tokens | (Random 32+ characters) |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime in minutes | `60` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime in days | `7` |
| `DATABASE_URL` | MySQL connection string | `mysql+pymysql://brightloop_app:change-me@localhost:3306/brightloop360?charset=utf8mb4` |
| `CORS_ORIGINS` | Allowed frontend origins (JSON or comma-separated) | `["http://localhost:3000","http://localhost:5173"]` |

---

## 3. Database Schema & Tables

All 23 tables are implemented using SQLAlchemy 2 declarative models in `backend/app/models/`:

1. **Identity & RBAC**:
   - `roles`: System roles (`Admin`, `Sales`, `Finance`, `Support`)
   - `permissions`: Fine-grained permission codes
   - `role_permissions`: Many-to-many junction table
   - `users`: User accounts with Argon2id hashed passwords
   - `refresh_tokens`: SHA-256 hashed rotation refresh tokens

2. **Customer Domain**:
   - `customers`: Individual and business customer profiles

3. **Catalog & Pricing**:
   - `products`: Product catalog entries
   - `product_variants`: Product variants with specific prices and JSON attributes
   - `plans`: Recurring subscription plans (day, week, month, year)
   - `plan_items`: Items included in recurring plans
   - `discounts`: Percentage or fixed discounts with redemption counters
   - `tax_rates`: Regional tax configurations (e.g., GST 18%, GST 5%)

4. **Quotations**:
   - `quotations`: Sales quotes with totals, discounts, and statuses
   - `quotation_items`: Line items with price and tax snapshots

5. **Subscriptions**:
   - `subscriptions`: Recurring subscriptions with period tracking
   - `subscription_items`: Subscription product line snapshots
   - `subscription_events`: Lifecycle transition audit logs

6. **Invoicing & Payments**:
   - `invoices`: Subscription, one-time, or adjustment invoices with customer & address snapshots
   - `invoice_items`: Immutable price, discount, and tax rate snapshots
   - `payments`: Customer payments with idempotency keys
   - `payment_allocations`: Payments allocated to invoices (M:N)
   - `billing_runs`: Automated recurring billing period records

7. **Compliance**:
   - `audit_logs`: Immutable entity audit trail

---

## 4. Setup & Running Instructions

### Step 1: Create and Activate Virtual Environment
```bash
cd backend
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt):
.\venv\Scripts\activate.bat

# Linux / macOS:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Database Migrations
Ensure MySQL 8 is running and database `brightloop360` exists, then run:
```bash
alembic upgrade head
```

### Step 4: Seed Database
Populates standard roles, permissions, demo users (`admin@brightloop.io`, `sales@brightloop.io`, `finance@brightloop.io`), demo taxes, and catalog starter items:
```bash
python -m app.utils.seed
```

### Step 5: Start FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger API documentation is available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 5. Running Automated Tests

Run the test suite using SQLite in-memory database:
```bash
pytest app/tests -v
```

---

## 6. Authentication API Contract (For Person 3 & Person 4)

### `POST /api/v1/auth/login`
- **Request Body**:
```json
{
  "email": "admin@brightloop.io",
  "password": "Admin@12345"
}
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1Ni...",
  "refresh_token": "uRk9sM...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "full_name": "System Administrator",
    "email": "admin@brightloop.io",
    "is_active": true,
    "role": {
      "id": 1,
      "name": "Admin",
      "description": "Full system administrator with unrestricted access",
      "permissions": ["catalog:read", "catalog:write", "customer:read", ...]
    },
    "permissions": ["catalog:read", "catalog:write", "customer:read", ...],
    "last_login_at": "2026-10-31T11:40:00",
    "created_at": "2026-10-31T11:30:00"
  }
}
```

### `GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response `200 OK`**: Returns authenticated user profile, assigned role, and permissions list.

### `POST /api/v1/auth/refresh`
- **Request Body**:
```json
{
  "refresh_token": "uRk9sM..."
}
```
- **Response `200 OK`**: Rotates the refresh token and returns a newly issued access token and rotated refresh token.

### `POST /api/v1/auth/logout`
- **Request Body**:
```json
{
  "refresh_token": "uRk9sM..."
}
```
- **Response `200 OK`**: Revokes the refresh token.

---

## 7. Demo Accounts

| Role | Email | Password | Granted Permissions |
|---|---|---|---|
| **Admin** | `admin@brightloop.io` | `Admin@12345` | Unrestricted (all permissions + Admin bypass) |
| **Sales** | `sales@brightloop.io` | `Sales@12345` | Customers, Quotations, Subscriptions, Catalog, Dashboard |
| **Finance** | `finance@brightloop.io` | `Finance@12345` | Customers, Subscriptions, Invoices, Payments, Dashboard |

