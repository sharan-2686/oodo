# Migrations

Initialize Alembic once with `alembic init alembic`, then configure its `env.py` to import `app.models` and use `Base.metadata`. The starter deliberately does not include a generated initial migration because it must be generated against the team-approved schema after the unresolved PRD choices (tenanting, GST/e-invoicing, refunds and webhooks) are settled.
