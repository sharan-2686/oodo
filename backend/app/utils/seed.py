from decimal import Decimal
import sys
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_utc_now
from app.core.security import hash_password
from app.models.catalog import (
    BillingInterval,
    Discount,
    DiscountType,
    Plan,
    PlanItem,
    Product,
    ProductVariant,
    TaxRate,
)
from app.models.user import Permission, Role, User

# Permission definitions: (code, description)
PERMISSIONS_DATA = [
    # Catalog
    ("catalog:read", "View products, variants, plans, tax rates, and discounts"),
    ("catalog:write", "Create, edit, or toggle products, plans, and discounts"),
    # Customers
    ("customer:read", "View customer profiles and lists"),
    ("customer:write", "Create and edit customer records"),
    ("customer:delete", "Deactivate customer accounts"),
    # Quotations
    ("quotation:read", "View quotations and item lists"),
    ("quotation:write", "Create and draft quotations"),
    ("quotation:convert", "Convert accepted quotations to active subscriptions"),
    # Subscriptions
    ("subscription:read", "View subscriptions, items, and event history"),
    ("subscription:write", "Create or edit subscription configurations"),
    ("subscription:cancel", "Cancel subscriptions and manage lifecycle transitions"),
    # Invoices
    ("invoice:read", "View invoices, line item snapshots, and payment status"),
    ("invoice:write", "Create manual or one-time invoices"),
    ("invoice:void", "Void or mark invoices uncollectible"),
    # Payments
    ("payments:read", "View recorded payments and allocation breakdown"),
    ("payments:write", "Record payments and allocate to invoices"),
    ("payments:refund", "Process payment refunds"),
    # Dashboard
    ("dashboard:read", "Access executive business intelligence and KPI metrics"),
    # User Management
    ("users:read", "View internal users and role assignments"),
    ("users:write", "Create and manage internal employee accounts"),
    ("roles:read", "View system roles and permission sets"),
    # Audit
    ("audit:read", "Inspect immutable compliance audit logs"),
]

# Role definitions: (name, description, permission_codes)
ROLES_DATA = {
    "Admin": {
        "description": "Full system administrator with unrestricted access",
        "permissions": [p[0] for p in PERMISSIONS_DATA],  # All permissions
    },
    "Sales": {
        "description": "Sales representative managing customers, quotations, and subscriptions",
        "permissions": [
            "catalog:read",
            "customer:read",
            "customer:write",
            "quotation:read",
            "quotation:write",
            "quotation:convert",
            "subscription:read",
            "subscription:write",
            "invoice:read",
            "dashboard:read",
        ],
    },
    "Finance": {
        "description": "Finance and accounting specialist managing invoices and payments",
        "permissions": [
            "customer:read",
            "subscription:read",
            "invoice:read",
            "invoice:write",
            "invoice:void",
            "payments:read",
            "payments:write",
            "payments:refund",
            "dashboard:read",
        ],
    },
    "Support": {
        "description": "Customer support specialist with read and inspection access",
        "permissions": [
            "catalog:read",
            "customer:read",
            "quotation:read",
            "subscription:read",
            "invoice:read",
            "payments:read",
        ],
    },
}

# Initial seed users: (email, password, full_name, role_name)
USERS_DATA = [
    ("admin@brightloop.io", "Admin@12345", "System Administrator", "Admin"),
    ("sales@brightloop.io", "Sales@12345", "Sales Representative", "Sales"),
    ("finance@brightloop.io", "Finance@12345", "Finance Manager", "Finance"),
]

# Standard tax rates
TAX_RATES_DATA = [
    {"name": "GST 18%", "code": "GST_18", "rate_percent": Decimal("18.0000"), "country": "IN", "is_inclusive": False},
    {"name": "GST 5%", "code": "GST_5", "rate_percent": Decimal("5.0000"), "country": "IN", "is_inclusive": False},
    {"name": "Zero Tax (Exempt)", "code": "ZERO_TAX", "rate_percent": Decimal("0.0000"), "country": "IN", "is_inclusive": False},
]

# Demonstration discounts
DISCOUNTS_DATA = [
    {
        "code": "WELCOME20",
        "name": "Welcome 20% Off",
        "discount_type": DiscountType.PERCENTAGE,
        "discount_value": Decimal("20.00"),
        "max_redemptions": 500,
    },
    {
        "code": "FLAT500",
        "name": "Flat ₹500 Discount",
        "discount_type": DiscountType.FIXED,
        "discount_value": Decimal("500.00"),
        "currency": "INR",
        "max_redemptions": 100,
    },
]


def seed_database(db: Session) -> None:
    """Populate database with initial roles, permissions, users, and catalog demo data."""
    print("--> Seeding permissions...")
    perm_map = {}
    for code, desc in PERMISSIONS_DATA:
        perm = db.scalar(select(Permission).where(Permission.code == code))
        if not perm:
            perm = Permission(code=code, description=desc)
            db.add(perm)
            db.flush()
        perm_map[code] = perm

    print("--> Seeding roles and role_permissions...")
    role_map = {}
    for role_name, info in ROLES_DATA.items():
        role = db.scalar(select(Role).where(Role.name == role_name))
        if not role:
            role = Role(
                name=role_name,
                description=info["description"],
                created_at=get_utc_now(),
            )
            db.add(role)
            db.flush()
        # Associate permissions
        target_perms = [perm_map[code] for code in info["permissions"] if code in perm_map]
        role.permissions = target_perms
        role_map[role_name] = role

    print("--> Seeding demonstration users...")
    for email, password, full_name, role_name in USERS_DATA:
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            role = role_map.get(role_name)
            if not role:
                continue
            user = User(
                email=email,
                password_hash=hash_password(password),
                full_name=full_name,
                role_id=role.id,
                is_active=True,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            )
            db.add(user)

    print("--> Seeding tax rates...")
    for tax_info in TAX_RATES_DATA:
        tax = db.scalar(select(TaxRate).where(TaxRate.code == tax_info["code"]))
        if not tax:
            tax = TaxRate(
                name=tax_info["name"],
                code=tax_info["code"],
                rate_percent=tax_info["rate_percent"],
                country=tax_info["country"],
                is_inclusive=tax_info["is_inclusive"],
                is_active=True,
                created_at=get_utc_now(),
            )
            db.add(tax)

    print("--> Seeding discounts...")
    for disc_info in DISCOUNTS_DATA:
        disc = db.scalar(select(Discount).where(Discount.code == disc_info["code"]))
        if not disc:
            disc = Discount(
                code=disc_info["code"],
                name=disc_info["name"],
                discount_type=disc_info["discount_type"],
                discount_value=disc_info["discount_value"],
                currency=disc_info.get("currency"),
                max_redemptions=disc_info.get("max_redemptions"),
                redemption_count=0,
                is_active=True,
                created_at=get_utc_now(),
            )
            db.add(disc)

    print("--> Seeding catalog products and plans...")
    # Starter Workspace Product
    starter_prod = db.scalar(select(Product).where(Product.sku == "PROD-WORKSPACE"))
    if not starter_prod:
        starter_prod = Product(
            sku="PROD-WORKSPACE",
            name="Brightloop Workspace",
            description="All-in-one cloud workspace suite",
            category="SaaS",
            is_active=True,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(starter_prod)
        db.flush()

        # Variant
        starter_var = ProductVariant(
            product_id=starter_prod.id,
            sku="VAR-WORKSPACE-STD",
            name="Workspace Standard Seat",
            unit_price=Decimal("499.00"),
            currency="INR",
            is_active=True,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(starter_var)
        db.flush()

        # Plan
        starter_plan = Plan(
            code="PLAN-WORKSPACE-MONTHLY",
            name="Workspace Monthly Plan",
            description="Monthly subscription for Brightloop Workspace",
            billing_interval=BillingInterval.MONTH,
            interval_count=1,
            base_price=Decimal("499.00"),
            currency="INR",
            trial_days=14,
            is_active=True,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(starter_plan)
        db.flush()

        plan_item = PlanItem(
            plan_id=starter_plan.id,
            product_id=starter_prod.id,
            variant_id=starter_var.id,
            quantity=Decimal("1.000"),
            unit_price=Decimal("499.00"),
            created_at=get_utc_now(),
        )
        db.add(plan_item)

    db.commit()
    print("--> Database seeding completed successfully!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}", file=sys.stderr)
        raise
    finally:
        db.close()

