# RuleLock AI - Transaction Monitoring and Data Collection

Owner: Charuka. This service runs on port `5001`, serves the existing demo
storefront, records sessions and events in the existing Supabase database, and forwards checkout
data to the rule and anomaly services when their URLs are configured.

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

This component does not create or migrate a database. It connects to the
existing Cakely Supabase project and writes to its existing `products` and
`transaction_events` tables using the server-only `SUPABASE_SECRET_KEY`.
It does not use or create a separate PostgreSQL database or an `audit_log`
table.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Demo storefront frontend |
| GET | `/health` | Liveness check |
| GET | `/browse` | List demo products |
| POST | `/cart` | Calculate a cart, and log it when `session_id` is supplied |
| POST | `/apply-coupon` | Apply a coupon, and log the attempt when `session_id` is supplied |
| POST | `/checkout` | Log checkout, call rule/anomaly services, and return their results |
| POST | `/review-order` | Secured Cakely pre-payment review endpoint |
| GET/POST | `/settings/rulelock` | Secured owner-toggle endpoint backed by Cakely `platform_settings` |

`RULE_ENGINE_URL` and `ANOMALY_ENGINE_URL` are optional. When unset or
unreachable, checkout uses local pass-through stubs so the service remains
usable during local development.

`/review-order` returns a normalized Cakely handoff:

```json
{
  "decision": "accept",
  "payment_action": "capture_payment",
  "cakely_order_status": "approved_for_payment"
}
```

For `hold`, Cakely should not capture payment and should show the order as
`review`. For `reject`, Cakely should not capture payment and should show the
order as `blocked`.
