"""Razorpay columns and webhook events table

Revision ID: 0002_razorpay
Revises: 
Create Date: 2026-10-31

Adds:
  - payments.razorpay_order_id  VARCHAR(50) UNIQUE NULL
  - payments.razorpay_payment_id VARCHAR(50) UNIQUE NULL
  - payments.failure_reason TEXT NULL
  - razorpay_webhook_events table (for webhook deduplication)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '0002_razorpay'
down_revision = None  # Update this to the actual previous revision ID if chaining
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. Extend payments table with Razorpay columns ─────────────────────
    op.add_column(
        'payments',
        sa.Column('razorpay_order_id', sa.String(50), nullable=True)
    )
    op.add_column(
        'payments',
        sa.Column('razorpay_payment_id', sa.String(50), nullable=True)
    )
    op.add_column(
        'payments',
        sa.Column('failure_reason', sa.Text(), nullable=True)
    )

    # Unique constraints (prevent duplicate Razorpay IDs)
    op.create_unique_constraint(
        'uq_payment_razorpay_order_id', 'payments', ['razorpay_order_id']
    )
    op.create_unique_constraint(
        'uq_payment_razorpay_payment_id', 'payments', ['razorpay_payment_id']
    )

    # Indexes for fast lookup
    op.create_index(
        'ix_payments_razorpay_order_id', 'payments', ['razorpay_order_id'], unique=True
    )
    op.create_index(
        'ix_payments_razorpay_payment_id', 'payments', ['razorpay_payment_id'], unique=True
    )

    # ── 2. Create razorpay_webhook_events table ─────────────────────────────
    op.create_table(
        'razorpay_webhook_events',
        sa.Column('id', sa.BigInteger().with_variant(mysql.BIGINT(unsigned=True), 'mysql'), primary_key=True, autoincrement=True),
        sa.Column('razorpay_event_id', sa.String(100), nullable=False),
        sa.Column('event_type', sa.String(60), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='processing'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('razorpay_event_id', name='uq_razorpay_event_id'),
        sa.PrimaryKeyConstraint('id'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
    )
    op.create_index(
        'ix_webhook_event_type', 'razorpay_webhook_events', ['event_type']
    )
    op.create_index(
        'ix_webhook_status', 'razorpay_webhook_events', ['status']
    )
    op.create_index(
        'ix_webhook_razorpay_event_id', 'razorpay_webhook_events', ['razorpay_event_id'], unique=True
    )


def downgrade() -> None:
    # ── Drop razorpay_webhook_events table ──────────────────────────────────
    op.drop_index('ix_webhook_razorpay_event_id', table_name='razorpay_webhook_events')
    op.drop_index('ix_webhook_status', table_name='razorpay_webhook_events')
    op.drop_index('ix_webhook_event_type', table_name='razorpay_webhook_events')
    op.drop_table('razorpay_webhook_events')

    # ── Remove Razorpay columns from payments ───────────────────────────────
    op.drop_index('ix_payments_razorpay_payment_id', table_name='payments')
    op.drop_index('ix_payments_razorpay_order_id', table_name='payments')
    op.drop_constraint('uq_payment_razorpay_payment_id', 'payments', type_='unique')
    op.drop_constraint('uq_payment_razorpay_order_id', 'payments', type_='unique')
    op.drop_column('payments', 'failure_reason')
    op.drop_column('payments', 'razorpay_payment_id')
    op.drop_column('payments', 'razorpay_order_id')
