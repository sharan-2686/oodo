from decimal import Decimal
from datetime import date, timedelta

def test_full_business_workflow(client):
    # 1. Create Customer
    customer_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_code": "CUST-001",
            "customer_type": "business",
            "name": "Acme Technologies Corp",
            "email": "billing@acme.com",
            "phone": "+91 9876543210",
            "company_name": "Acme Inc",
            "billing_address_line1": "100 Tech Park",
            "billing_city": "Bengaluru",
            "billing_state": "Karnataka",
            "billing_postal_code": "560001",
            "billing_country": "IN"
        }
    )
    assert customer_resp.status_code == 201, customer_resp.text
    cust_data = customer_resp.json()
    cust_id = cust_data["id"]
    assert cust_data["customer_code"] == "CUST-001"

    # Duplicate customer code should fail
    dup_cust = client.post(
        "/api/v1/customers",
        json={"customer_code": "CUST-001", "name": "Duplicate"}
    )
    assert dup_cust.status_code == 400

    # 2. Create Product with Variant
    product_resp = client.post(
        "/api/v1/products",
        json={
            "sku": "PROD-ERP",
            "name": "Brightloop ERP Cloud",
            "description": "Core ERP software seat",
            "category": "Software",
            "variants": [
                {
                    "sku": "PROD-ERP-ODOO",
                    "name": "Brightloop ERP - Odoo Edition",
                    "attributes": {"brand": "Odoo"},
                    "unit_price": "1560.00"
                }
            ]
        }
    )
    assert product_resp.status_code == 201, product_resp.text
    prod_data = product_resp.json()
    prod_id = prod_data["id"]
    variant_id = prod_data["variants"][0]["id"]
    assert prod_data["variants"][0]["unit_price"] == "1560.00"

    # 3. Create Billing Plan
    plan_resp = client.post(
        "/api/v1/plans",
        json={
            "code": "PLAN-MONTHLY-BIZ",
            "name": "Business Monthly Plan",
            "billing_interval": "month",
            "interval_count": 1,
            "base_price": "1560.00",
            "currency": "INR",
            "items": [
                {
                    "product_id": prod_id,
                    "variant_id": variant_id,
                    "quantity": "1.000",
                    "unit_price": "1560.00"
                }
            ]
        }
    )
    assert plan_resp.status_code == 201, plan_resp.text
    plan_data = plan_resp.json()
    plan_id = plan_data["id"]

    # 4. Create Discount
    discount_resp = client.post(
        "/api/v1/discounts",
        json={
            "code": "PROMO10",
            "name": "10 Percent Launch Discount",
            "discount_type": "percentage",
            "discount_value": "10.00",
            "max_redemptions": 100
        }
    )
    assert discount_resp.status_code == 201, discount_resp.text
    disc_id = discount_resp.json()["id"]

    # 5. Create Quotation
    quote_resp = client.post(
        "/api/v1/quotations",
        json={
            "customer_id": cust_id,
            "discount_id": disc_id,
            "currency": "INR",
            "terms": "Payment due within 15 days",
            "items": [
                {
                    "product_id": prod_id,
                    "variant_id": variant_id,
                    "plan_id": plan_id,
                    "description": "Brightloop ERP Cloud - Odoo Edition 1 User",
                    "quantity": "2.000",
                    "unit_price": "1560.00",
                    "tax_rate_percent": "18.0000"
                }
            ]
        }
    )
    assert quote_resp.status_code == 201, quote_resp.text
    quote_data = quote_resp.json()
    quote_id = quote_data["id"]
    # Subtotal = 2 * 1560 = 3120.00
    # Tax = 18% of 3120 = 561.60
    # Discount = 10% of 3120 = 312.00
    # Total = 3120 - 312 + 561.60 = 3369.60
    assert quote_data["subtotal"] == "3120.00"
    assert quote_data["discount_amount"] == "312.00"
    assert quote_data["tax_amount"] == "561.60"
    assert quote_data["total_amount"] == "3369.60"
    assert quote_data["status"] == "draft"

    # Transition quotation status to accepted
    accept_resp = client.post(f"/api/v1/quotations/{quote_id}/status?status_value=sent")
    assert accept_resp.status_code == 200
    accept_resp = client.post(f"/api/v1/quotations/{quote_id}/status?status_value=accepted")
    assert accept_resp.status_code == 200

    # 6. Convert Quotation into Subscription
    convert_resp = client.post(
        f"/api/v1/quotations/{quote_id}/convert",
        json={"plan_id": plan_id, "billing_interval": "month"}
    )
    assert convert_resp.status_code == 201, convert_resp.text
    sub_data = convert_resp.json()
    sub_id = sub_data["id"]
    assert sub_data["status"] == "active"
    assert sub_data["quotation_id"] == quote_id
    assert len(sub_data["items"]) == 1
    assert len(sub_data["events"]) >= 1

    # Verify duplicate conversion is strictly PREVENTED
    dup_convert = client.post(
        f"/api/v1/quotations/{quote_id}/convert",
        json={"plan_id": plan_id}
    )
    assert dup_convert.status_code == 400
    assert "already been converted" in dup_convert.json()["detail"]

    # 7. Generate Invoice from Subscription
    inv_resp = client.post(
        "/api/v1/invoices/generate-from-subscription",
        json={
            "subscription_id": sub_id,
            "billing_period_start": str(date.today()),
            "billing_period_end": str(date.today() + timedelta(days=30))
        }
    )
    assert inv_resp.status_code == 201, inv_resp.text
    inv_data = inv_resp.json()
    inv_id = inv_data["id"]
    assert inv_data["status"] == "issued"
    assert inv_data["customer_name_snapshot"] == "Acme Technologies Corp"
    assert inv_data["discount_code_snapshot"] == "PROMO10"
    assert inv_data["total_amount"] == "2808.00" # items inherit plan price/subtotal minus 10% discount
    assert inv_data["balance_due"] == "2808.00"

    # Verify duplicate invoice generation for the same billing period is PREVENTED
    dup_inv = client.post(
        "/api/v1/invoices/generate-from-subscription",
        json={
            "subscription_id": sub_id,
            "billing_period_start": str(date.today()),
            "billing_period_end": str(date.today() + timedelta(days=30))
        }
    )
    assert dup_inv.status_code == 400
    assert "Invoice already generated" in dup_inv.json()["detail"]

    # 8. Record Payment & Allocations
    # Test allocating to invoice belonging to a different customer should fail
    cust2_resp = client.post(
        "/api/v1/customers",
        json={"customer_code": "CUST-002", "name": "Other Corp"}
    )
    cust2_id = cust2_resp.json()["id"]
    mismatch_pay = client.post(
        "/api/v1/payments",
        json={
            "customer_id": cust2_id,
            "amount": "1000.00",
            "allocations": [{"invoice_id": inv_id, "amount": "1000.00"}]
        }
    )
    assert mismatch_pay.status_code == 400
    assert "belongs to customer" in mismatch_pay.json()["detail"]

    # Test allocation exceeding payment amount should fail
    over_pay = client.post(
        "/api/v1/payments",
        json={
            "customer_id": cust_id,
            "amount": "1000.00",
            "allocations": [{"invoice_id": inv_id, "amount": "1500.00"}]
        }
    )
    assert over_pay.status_code == 400

    # Successful Partial Payment (2000.00 out of 2808.00)
    pay1_resp = client.post(
        "/api/v1/payments",
        json={
            "customer_id": cust_id,
            "amount": "2000.00",
            "payment_method": "bank_transfer",
            "transaction_reference": "TXN-BANK-12345",
            "idempotency_key": "IDEM-KEY-001",
            "allocations": [{"invoice_id": inv_id, "amount": "2000.00"}]
        }
    )
    assert pay1_resp.status_code == 201, pay1_resp.text
    pay1_data = pay1_resp.json()
    assert pay1_data["total_allocated"] == "2000.00"

    # Check updated invoice status (partially_paid)
    check_inv1 = client.get(f"/api/v1/invoices/{inv_id}").json()
    assert check_inv1["status"] == "partially_paid"
    assert check_inv1["amount_paid"] == "2000.00"
    assert check_inv1["balance_due"] == "808.00"

    # Idempotent re-submission should return original payment
    re_pay = client.post(
        "/api/v1/payments",
        json={
            "customer_id": cust_id,
            "amount": "2000.00",
            "idempotency_key": "IDEM-KEY-001"
        }
    )
    assert re_pay.status_code in [200, 201]
    assert re_pay.json()["id"] == pay1_data["id"]

    # Successful Final Payment (Remaining 808.00)
    pay2_resp = client.post(
        "/api/v1/payments",
        json={
            "customer_id": cust_id,
            "amount": "808.00",
            "payment_method": "upi",
            "transaction_reference": "UPI-REF-9988",
            "allocations": [{"invoice_id": inv_id, "amount": "808.00"}]
        }
    )
    assert pay2_resp.status_code == 201, pay2_resp.text
    
    # Check invoice status is now 'paid'
    check_inv2 = client.get(f"/api/v1/invoices/{inv_id}").json()
    assert check_inv2["status"] == "paid"
    assert check_inv2["balance_due"] == "0.00"

    # 9. Test Subscription Lifecycle Actions
    pause_resp = client.post(
        f"/api/v1/subscriptions/{sub_id}/lifecycle",
        json={"action": "pause", "reason": "Customer seasonal hold"}
    )
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    resume_resp = client.post(
        f"/api/v1/subscriptions/{sub_id}/lifecycle",
        json={"action": "resume"}
    )
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "active"

    cancel_resp = client.post(
        f"/api/v1/subscriptions/{sub_id}/cancel?reason=Project%20completed"
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "cancelled"

    # 10. Test Dashboard Summary KPIs
    dash_resp = client.get("/api/v1/dashboard/summary")
    assert dash_resp.status_code == 200, dash_resp.text
    dash_data = dash_resp.json()
    assert "total_revenue_collected" in dash_data
    assert Decimal(dash_data["total_revenue_collected"]) == Decimal("2808.00")
    assert "subscriptions_by_status" in dash_data
    assert dash_data["subscriptions_by_status"]["cancelled"] == 1
