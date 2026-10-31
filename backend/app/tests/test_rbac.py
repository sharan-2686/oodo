import pytest
from app.core.security import hash_password
from app.models.user import User, Role, Permission

def test_rbac_and_signup_workflows(client, db_session):
    # 0. Seed basic roles and admin user
    admin_role = Role(name="admin", description="Full Admin")
    staff_role = Role(name="staff", description="Staff")
    sales_role = Role(name="sales", description="Sales Staff")
    cust_role = Role(name="Customer", description="Customer")

    # Add permissions
    p_cat_r = Permission(code="catalog:read", description="Read catalog")
    p_cat_w = Permission(code="catalog:write", description="Write catalog")
    p_u_w = Permission(code="users:write", description="Write users")
    p_u_r = Permission(code="users:read", description="Read users")
    db_session.add_all([admin_role, staff_role, sales_role, cust_role, p_cat_r, p_cat_w, p_u_w, p_u_r])
    db_session.flush()

    admin_role.permissions.extend([p_cat_r, p_cat_w, p_u_w, p_u_r])
    sales_role.permissions.append(p_cat_r)
    cust_role.permissions.append(p_cat_r)

    admin_user = User(
        email="admin@brightloop.io",
        password_hash=hash_password("Admin@12345"),
        full_name="Master Admin",
        role_id=admin_role.id,
        is_active=True
    )
    db_session.add(admin_user)
    db_session.commit()

    # --- 1. Admin Direct Login (Admin does NOT need signup) ---
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@brightloop.io", "password": "Admin@12345"}
    )
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # --- 2. Staff Signup (Admin cannot be self-registered) ---
    bad_admin_signup = client.post(
        "/api/v1/auth/signup/staff",
        json={
            "email": "hacker@brightloop.io",
            "password": "Password123!",
            "full_name": "Fake Admin",
            "role": "admin"
        }
    )
    assert bad_admin_signup.status_code == 403
    assert "cannot be self-registered" in bad_admin_signup.json()["detail"]

    # Valid Staff Signup (Sales)
    staff_signup = client.post(
        "/api/v1/auth/signup/staff",
        json={
            "email": "john.sales@brightloop.io",
            "password": "Password123!",
            "full_name": "John Sales",
            "role": "sales"
        }
    )
    assert staff_signup.status_code == 201
    staff_token = staff_signup.json()["access_token"]
    staff_headers = {"Authorization": f"Bearer {staff_token}"}

    # --- 3. Customer Signup (Self-service + auto-profile creation) ---
    cust_signup = client.post(
        "/api/v1/auth/signup/customer",
        json={
            "email": "client@enterprise.com",
            "password": "ClientPassword123!",
            "full_name": "Enterprise Client",
            "customer_type": "business",
            "company_name": "Enterprise Ltd",
            "phone": "+91 9999988888"
        }
    )
    assert cust_signup.status_code == 201
    cust_token = cust_signup.json()["access_token"]
    cust_headers = {"Authorization": f"Bearer {cust_token}"}
    cust_id = cust_signup.json()["user"]["id"]

    # --- 4. Catalog Management: Only Admin can create/modify/delete products ---
    # Staff tries to create product -> 403 Forbidden
    staff_prod_fail = client.post(
        "/api/v1/products",
        headers=staff_headers,
        json={"sku": "PROD-STAFF-FAIL", "name": "Staff Product"}
    )
    assert staff_prod_fail.status_code == 403

    # Customer tries to create product -> 403 Forbidden
    cust_prod_fail = client.post(
        "/api/v1/products",
        headers=cust_headers,
        json={"sku": "PROD-CUST-FAIL", "name": "Cust Product"}
    )
    assert cust_prod_fail.status_code == 403

    # Admin creates product -> 201 Success
    admin_prod_resp = client.post(
        "/api/v1/products",
        headers=admin_headers,
        json={
            "sku": "PROD-CLOUD-ERP",
            "name": "Cloud ERP",
            "category": "SaaS",
            "variants": [
                {
                    "sku": "VAR-ERP-BASE",
                    "name": "ERP Base License",
                    "unit_price": "1000.00"
                }
            ]
        }
    )
    assert admin_prod_resp.status_code == 201
    prod_data = admin_prod_resp.json()
    prod_id = prod_data["id"]

    # Admin can add variant
    var_resp = client.post(
        f"/api/v1/products/{prod_id}/variants",
        headers=admin_headers,
        json={"sku": "VAR-ERP-ADDON", "name": "Extra Storage", "unit_price": "200.00"}
    )
    assert var_resp.status_code == 201
    var_id = var_resp.json()["id"]

    # Admin creates recurring plan
    plan_resp = client.post(
        "/api/v1/plans",
        headers=admin_headers,
        json={
            "code": "PLAN-ERP-MONTHLY",
            "name": "Cloud ERP Monthly",
            "billing_interval": "month",
            "base_price": "1000.00"
        }
    )
    assert plan_resp.status_code == 201

    # --- 5. Customer Buying Flow ---
    # Customer browses products -> 200 OK
    browse = client.get("/api/v1/products", headers=cust_headers)
    assert browse.status_code == 200
    assert len(browse.json()) >= 1

    # Customer creates quotation to buy products -> 201 Created
    quote_resp = client.post(
        "/api/v1/quotations",
        headers=cust_headers,
        json={
            "currency": "INR",
            "items": [
                {
                    "product_id": prod_id,
                    "description": "Cloud ERP Subscription Purchase",
                    "quantity": "2.000",
                    "unit_price": "1000.00"
                }
            ]
        }
    )
    assert quote_resp.status_code == 201
    quote_id = quote_resp.json()["id"]

    # Customer accepts the quotation -> 200 OK
    accept_resp = client.post(
        f"/api/v1/quotations/{quote_id}/status?status_value=accepted",
        headers=cust_headers
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

    # Customer cannot convert quotation directly to subscription -> 403 Forbidden
    cust_convert_fail = client.post(
        f"/api/v1/quotations/{quote_id}/convert",
        headers=cust_headers,
        json={"billing_interval": "month"}
    )
    assert cust_convert_fail.status_code == 403

    # Staff converts accepted quotation to active subscription -> 201 Created
    staff_convert = client.post(
        f"/api/v1/quotations/{quote_id}/convert",
        headers=staff_headers,
        json={"billing_interval": "month"}
    )
    assert staff_convert.status_code == 201
    sub_data = staff_convert.json()
    assert sub_data["status"] == "active"

    # Customer tries to create invoice directly -> 403 Forbidden
    cust_inv_fail = client.post(
        "/api/v1/invoices",
        headers=cust_headers,
        json={
            "customer_id": quote_resp.json()["customer_id"],
            "items": [{"description_snapshot": "Custom item", "quantity": "1.000", "unit_price": "500.00"}]
        }
    )
    assert cust_inv_fail.status_code == 403

    # Staff generates invoice -> 201 Created
    staff_inv = client.post(
        "/api/v1/invoices",
        headers=staff_headers,
        json={
            "customer_id": quote_resp.json()["customer_id"],
            "items": [{"description_snapshot": "ERP First Month", "quantity": "2.000", "unit_price": "1000.00"}]
        }
    )
    assert staff_inv.status_code == 201
    inv_id = staff_inv.json()["id"]

    # Customer pays invoice -> 201 Created
    cust_pay = client.post(
        "/api/v1/payments",
        headers=cust_headers,
        json={
            "customer_id": quote_resp.json()["customer_id"],
            "amount": "2000.00",
            "payment_method": "card",
            "allocations": [{"invoice_id": inv_id, "amount": "2000.00"}]
        }
    )
    assert cust_pay.status_code == 201
    assert cust_pay.json()["status"] == "succeeded"

    # Customer can only view their own invoices
    my_invoices = client.get("/api/v1/invoices", headers=cust_headers)
    assert my_invoices.status_code == 200
    assert len(my_invoices.json()) == 1
    assert my_invoices.json()[0]["id"] == inv_id
