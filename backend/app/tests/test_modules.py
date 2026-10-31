from decimal import Decimal
from datetime import date, timedelta

def test_customers_crud_and_search(client):
    r = client.post(
        "/api/v1/customers",
        json={
            "customer_code": "CUST-INDIV-1",
            "customer_type": "individual",
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+91 9123456780"
        }
    )
    assert r.status_code == 201
    cid = r.json()["id"]

    search_r = client.get("/api/v1/customers?search=Jane")
    assert search_r.status_code == 200
    assert search_r.json()["total"] >= 1
    assert any(c["id"] == cid for c in search_r.json()["items"])

    upd_r = client.put(f"/api/v1/customers/{cid}", json={"company_name": "Jane Consulting"})
    assert upd_r.status_code == 200
    assert upd_r.json()["company_name"] == "Jane Consulting"

def test_subscription_lifecycle_transitions(client):
    c = client.post("/api/v1/customers", json={"customer_code": "CUST-SUB-TEST", "name": "Sub Tester"}).json()
    p = client.post("/api/v1/products", json={"sku": "SKU-SAAS", "name": "SaaS Platform"}).json()
    plan = client.post(
        "/api/v1/plans",
        json={
            "code": "PLAN-SAAS-MO",
            "name": "SaaS Monthly",
            "billing_interval": "month",
            "base_price": "500.00"
        }
    ).json()

    sub = client.post(
        "/api/v1/subscriptions",
        json={
            "customer_id": c["id"],
            "plan_id": plan["id"],
            "quantity": "3.000",
            "billing_interval": "month"
        }
    ).json()
    sub_id = sub["id"]
    assert sub["status"] == "active"

    # Pause
    r_pause = client.post(f"/api/v1/subscriptions/{sub_id}/lifecycle", json={"action": "pause", "reason": "Holiday"})
    assert r_pause.status_code == 200
    assert r_pause.json()["status"] == "paused"

    # Double pause rejected
    r_double_pause = client.post(f"/api/v1/subscriptions/{sub_id}/lifecycle", json={"action": "pause"})
    assert r_double_pause.status_code == 400

    # Resume
    r_resume = client.post(f"/api/v1/subscriptions/{sub_id}/lifecycle", json={"action": "resume"})
    assert r_resume.status_code == 200
    assert r_resume.json()["status"] == "active"

    # Renew
    r_renew = client.post(f"/api/v1/subscriptions/{sub_id}/lifecycle", json={"action": "renew"})
    assert r_renew.status_code == 200

    # Cancel
    r_cancel = client.post(f"/api/v1/subscriptions/{sub_id}/cancel")
    assert r_cancel.status_code == 200
    assert r_cancel.json()["status"] == "cancelled"

def test_one_time_invoice_and_actions(client):
    c = client.post("/api/v1/customers", json={"customer_code": "CUST-ONE-TIME", "name": "One Time Buyer"}).json()
    p = client.post("/api/v1/products", json={"sku": "PROD-CONSULT", "name": "Consulting Hour"}).json()

    inv = client.post(
        "/api/v1/invoices",
        json={
            "customer_id": c["id"],
            "notes": "Setup consultation",
            "items": [
                {
                    "product_id": p["id"],
                    "description_snapshot": "Onboarding consultation (4 hours)",
                    "quantity": "4.000",
                    "unit_price": "2500.00",
                    "tax_rate_percent": "18.0000"
                }
            ]
        }
    ).json()
    inv_id = inv["id"]
    assert inv["subtotal"] == "10000.00"
    assert inv["tax_amount"] == "1800.00"
    assert inv["total_amount"] == "11800.00"
    assert inv["status"] == "issued"

    void_r = client.post(f"/api/v1/invoices/{inv_id}/actions", json={"action": "void"})
    assert void_r.status_code == 200
    assert void_r.json()["status"] == "void"
