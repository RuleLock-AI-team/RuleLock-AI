-- RuleLock AI — PostgreSQL schema
-- Owner: Charuka (Component 1: Transaction Monitoring & Data Collection)

CREATE TABLE IF NOT EXISTS sessions (
    session_id      UUID PRIMARY KEY,
    device_id       TEXT,
    account_id      TEXT,
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        UUID PRIMARY KEY,
    session_id      UUID REFERENCES sessions(session_id),
    account_id      TEXT,
    account_verified BOOLEAN DEFAULT FALSE,
    payment_method  TEXT CHECK (payment_method IN ('COD', 'PREPAID')),
    subtotal        NUMERIC(12,2) NOT NULL,
    total           NUMERIC(12,2) NOT NULL,
    status          TEXT DEFAULT 'placed',
    created_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_items (
    id              SERIAL PRIMARY KEY,
    order_id        UUID REFERENCES orders(order_id),
    sku             TEXT NOT NULL,
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS discounts_applied (
    id              SERIAL PRIMARY KEY,
    order_id        UUID REFERENCES orders(order_id),
    coupon_code     TEXT NOT NULL,
    discount_value  NUMERIC(12,2) NOT NULL,
    applied_at      TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS delivery_outcomes (
    id              SERIAL PRIMARY KEY,
    order_id        UUID REFERENCES orders(order_id),
    outcome         TEXT CHECK (outcome IN ('delivered', 'refused', 'returned', 'pending')),
    recorded_at     TIMESTAMPTZ DEFAULT now()
);

-- Owner: Mishen (Component 4) — audit log for automated enforcement actions.
-- Lives here too since it's part of the same shared database.
CREATE TABLE IF NOT EXISTS audit_log (
    id              SERIAL PRIMARY KEY,
    order_id        TEXT,
    action          TEXT NOT NULL,
    reason          TEXT,
    "timestamp"     TIMESTAMPTZ DEFAULT now()
);
