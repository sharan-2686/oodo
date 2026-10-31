"""initial schema for Brightloop 360

Revision ID: 20261031_0001
Revises: 
Create Date: 2026-10-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "20261031_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. roles
    op.create_table(
        "roles",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(60), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_roles_name", "roles", ["name"])

    # 2. permissions
    op.create_table(
        "permissions",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("description", sa.String(255), nullable=True),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_permissions_code", "permissions", ["code"])

    # 3. role_permissions
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )

    # 4. users
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("role_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("last_login_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role_id", "users", ["role_id"])

    # 5. refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("revoked_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])

    # 6. customers
    op.create_table(
        "customers",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("customer_code", sa.String(40), nullable=False, unique=True),
        sa.Column("customer_type", sa.String(20), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("email", sa.String(254), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("company_name", sa.String(180), nullable=True),
        sa.Column("tax_identifier", sa.String(80), nullable=True),
        sa.Column("billing_address_line1", sa.String(255), nullable=True),
        sa.Column("billing_address_line2", sa.String(255), nullable=True),
        sa.Column("billing_city", sa.String(100), nullable=True),
        sa.Column("billing_state", sa.String(100), nullable=True),
        sa.Column("billing_postal_code", sa.String(30), nullable=True),
        sa.Column("billing_country", sa.String(2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_by", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_customers_customer_code", "customers", ["customer_code"])
    op.create_index("ix_customers_email", "customers", ["email"])
    op.create_index("ix_customers_phone", "customers", ["phone"])
    op.create_index("ix_customers_created_by", "customers", ["created_by"])

    # 7. products
    op.create_table(
        "products",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("sku", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_products_sku", "products", ["sku"])

    # 8. product_variants
    op.create_table(
        "product_variants",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sku", sa.String(80), nullable=False, unique=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("attributes", sa.JSON(), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("currency", sa.String(3), server_default="INR", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("unit_price >= 0", name="chk_variant_unit_price"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_product_variants_product_id", "product_variants", ["product_id"])
    op.create_index("ix_product_variants_sku", "product_variants", ["sku"])

    # 9. plans
    op.create_table(
        "plans",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(60), nullable=False, unique=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("billing_interval", sa.String(20), nullable=False),
        sa.Column("interval_count", sa.SmallInteger(), server_default=sa.text("1"), nullable=False),
        sa.Column("base_price", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("currency", sa.String(3), server_default="INR", nullable=False),
        sa.Column("trial_days", sa.SmallInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("interval_count >= 1", name="chk_plan_interval_count"),
        sa.CheckConstraint("base_price >= 0", name="chk_plan_base_price"),
        sa.CheckConstraint("trial_days >= 0", name="chk_plan_trial_days"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_plans_code", "plans", ["code"])

    # 10. plan_items
    op.create_table(
        "plan_items",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("plan_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("variant_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("quantity", sa.Numeric(12, 3), server_default=sa.text("1.000"), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("quantity > 0", name="chk_plan_item_quantity"),
        sa.CheckConstraint("unit_price >= 0", name="chk_plan_item_unit_price"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_plan_items_plan_id", "plan_items", ["plan_id"])
    op.create_index("ix_plan_items_product_id", "plan_items", ["product_id"])
    op.create_index("ix_plan_items_variant_id", "plan_items", ["variant_id"])

    # 11. discounts
    op.create_table(
        "discounts",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(60), nullable=False, unique=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("discount_type", sa.String(20), nullable=False),
        sa.Column("discount_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("starts_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("ends_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("max_redemptions", sa.Integer(), nullable=True),
        sa.Column("redemption_count", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("discount_value > 0", name="chk_discount_value"),
        sa.CheckConstraint("redemption_count >= 0", name="chk_discount_redemption_count"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_discounts_code", "discounts", ["code"])

    # 12. tax_rates
    op.create_table(
        "tax_rates",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("code", sa.String(40), nullable=False, unique=True),
        sa.Column("rate_percent", sa.Numeric(7, 4), nullable=False),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("is_inclusive", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("1"), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=True),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("rate_percent >= 0 AND rate_percent <= 100", name="chk_tax_rate_percent"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_tax_rates_code", "tax_rates", ["code"])

    # 13. quotations
    op.create_table(
        "quotations",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("quote_number", sa.String(50), nullable=False, unique=True),
        sa.Column("customer_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_by", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("discount_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("discounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(3), server_default="INR", nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("subtotal >= 0", name="chk_quote_subtotal"),
        sa.CheckConstraint("discount_amount >= 0", name="chk_quote_discount_amount"),
        sa.CheckConstraint("tax_amount >= 0", name="chk_quote_tax_amount"),
        sa.CheckConstraint("total_amount >= 0", name="chk_quote_total_amount"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_quotations_quote_number", "quotations", ["quote_number"])
    op.create_index("ix_quotations_customer_id", "quotations", ["customer_id"])
    op.create_index("ix_quotations_created_by", "quotations", ["created_by"])
    op.create_index("ix_quotations_discount_id", "quotations", ["discount_id"])

    # 14. quotation_items
    op.create_table(
        "quotation_items",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("quotation_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("quotations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("variant_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("plan_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), server_default=sa.text("1.000"), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_rate_percent", sa.Numeric(7, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("line_subtotal", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("line_tax", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("quantity > 0", name="chk_quote_item_quantity"),
        sa.CheckConstraint("unit_price >= 0", name="chk_quote_item_unit_price"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_quotation_items_quotation_id", "quotation_items", ["quotation_id"])

    # 15. subscriptions
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("subscription_number", sa.String(50), nullable=False, unique=True),
        sa.Column("customer_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("plan_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("plans.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quotation_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("quotations.id", ondelete="SET NULL"), unique=True, nullable=True),
        sa.Column("discount_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("discounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("currency", sa.String(3), server_default="INR", nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), server_default=sa.text("1.000"), nullable=False),
        sa.Column("billing_interval", sa.String(20), nullable=False),
        sa.Column("interval_count", sa.SmallInteger(), server_default=sa.text("1"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("trial_ends_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("current_period_start", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("current_period_end", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("next_billing_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("cancel_at_period_end", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("cancelled_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("created_by", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("unit_price >= 0", name="chk_sub_unit_price"),
        sa.CheckConstraint("quantity > 0", name="chk_sub_quantity"),
        sa.CheckConstraint("interval_count >= 1", name="chk_sub_interval_count"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_subscriptions_subscription_number", "subscriptions", ["subscription_number"])
    op.create_index("ix_subscriptions_customer_id", "subscriptions", ["customer_id"])
    op.create_index("ix_subscriptions_plan_id", "subscriptions", ["plan_id"])
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index("ix_subscriptions_next_billing_at", "subscriptions", ["next_billing_at"])

    # 16. subscription_items
    op.create_table(
        "subscription_items",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("subscription_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("variant_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description_snapshot", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), server_default=sa.text("1.000"), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("quantity > 0", name="chk_sub_item_quantity"),
        sa.CheckConstraint("unit_price >= 0", name="chk_sub_item_unit_price"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_subscription_items_subscription_id", "subscription_items", ["subscription_id"])

    # 17. subscription_events
    op.create_table(
        "subscription_events",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("subscription_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("from_status", sa.String(30), nullable=True),
        sa.Column("to_status", sa.String(30), nullable=True),
        sa.Column("event_data", sa.JSON(), nullable=True),
        sa.Column("actor_user_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_subscription_events_subscription_id", "subscription_events", ["subscription_id"])
    op.create_index("ix_subscription_events_event_type", "subscription_events", ["event_type"])

    # 18. invoices
    op.create_table(
        "invoices",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("invoice_number", sa.String(50), nullable=False, unique=True),
        sa.Column("customer_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("subscription_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("discount_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("discounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("invoice_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("currency", sa.String(3), server_default="INR", nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("billing_period_start", sa.Date(), nullable=True),
        sa.Column("billing_period_end", sa.Date(), nullable=True),
        sa.Column("subtotal", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_amount", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_amount", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_code_snapshot", sa.String(60), nullable=True),
        sa.Column("customer_name_snapshot", sa.String(180), nullable=False),
        sa.Column("customer_email_snapshot", sa.String(254), nullable=True),
        sa.Column("billing_address_snapshot", sa.JSON(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.Column("updated_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("subtotal >= 0", name="chk_invoice_subtotal"),
        sa.CheckConstraint("discount_amount >= 0", name="chk_invoice_discount_amount"),
        sa.CheckConstraint("tax_amount >= 0", name="chk_invoice_tax_amount"),
        sa.CheckConstraint("total_amount >= 0", name="chk_invoice_total_amount"),
        sa.CheckConstraint("due_date >= issue_date", name="chk_invoice_due_date"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"])
    op.create_index("ix_invoices_customer_id", "invoices", ["customer_id"])
    op.create_index("ix_invoices_subscription_id", "invoices", ["subscription_id"])
    op.create_index("ix_invoices_status", "invoices", ["status"])

    # 19. invoice_items
    op.create_table(
        "invoice_items",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("invoice_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("variant_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True),
        sa.Column("plan_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description_snapshot", sa.String(255), nullable=False),
        sa.Column("sku_snapshot", sa.String(80), nullable=True),
        sa.Column("quantity", sa.Numeric(12, 3), server_default=sa.text("1.000"), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_rate_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("tax_rates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tax_name_snapshot", sa.String(120), nullable=True),
        sa.Column("tax_rate_percent", sa.Numeric(7, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("line_subtotal", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("line_tax", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("quantity > 0", name="chk_invoice_item_quantity"),
        sa.CheckConstraint("unit_price >= 0", name="chk_invoice_item_unit_price"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_invoice_items_invoice_id", "invoice_items", ["invoice_id"])

    # 20. payments
    op.create_table(
        "payments",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("payment_number", sa.String(50), nullable=False, unique=True),
        sa.Column("customer_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="INR", nullable=False),
        sa.Column("payment_method", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("transaction_reference", sa.String(150), nullable=True),
        sa.Column("idempotency_key", sa.String(100), unique=True, nullable=True),
        sa.Column("paid_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("amount > 0", name="chk_payment_amount"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_payments_payment_number", "payments", ["payment_number"])
    op.create_index("ix_payments_customer_id", "payments", ["customer_id"])
    op.create_index("ix_payments_status", "payments", ["status"])
    op.create_index("ix_payments_idempotency_key", "payments", ["idempotency_key"])

    # 21. payment_allocations
    op.create_table(
        "payment_allocations",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("payment_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("payments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invoice_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount_allocated", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.CheckConstraint("amount_allocated > 0", name="chk_alloc_amount"),
        sa.UniqueConstraint("payment_id", "invoice_id", name="uq_payment_invoice_alloc"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_payment_allocations_payment_id", "payment_allocations", ["payment_id"])
    op.create_index("ix_payment_allocations_invoice_id", "payment_allocations", ["invoice_id"])

    # 22. billing_runs
    op.create_table(
        "billing_runs",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("subscription_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("invoice_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("invoices.id", ondelete="SET NULL"), unique=True, nullable=True),
        sa.Column("billing_period_start", sa.Date(), nullable=False),
        sa.Column("billing_period_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("attempt_count", sa.SmallInteger(), server_default=sa.text("0"), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("completed_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        sa.UniqueConstraint("subscription_id", "billing_period_start", "billing_period_end", name="uq_sub_billing_period"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_billing_runs_subscription_id", "billing_runs", ["subscription_id"])
    op.create_index("ix_billing_runs_invoice_id", "billing_runs", ["invoice_id"])

    # 23. audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), primary_key=True, autoincrement=True),
        sa.Column("actor_user_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("entity_type", sa.String(80), nullable=False),
        sa.Column("entity_id", sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), "mysql"), nullable=True),
        sa.Column("before_data", sa.JSON(), nullable=True),
        sa.Column("after_data", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"), nullable=False),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_entity_type", "audit_logs", ["entity_type"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("billing_runs")
    op.drop_table("payment_allocations")
    op.drop_table("payments")
    op.drop_table("invoice_items")
    op.drop_table("invoices")
    op.drop_table("subscription_events")
    op.drop_table("subscription_items")
    op.drop_table("subscriptions")
    op.drop_table("quotation_items")
    op.drop_table("quotations")
    op.drop_table("tax_rates")
    op.drop_table("discounts")
    op.drop_table("plan_items")
    op.drop_table("plans")
    op.drop_table("product_variants")
    op.drop_table("products")
    op.drop_table("customers")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")

