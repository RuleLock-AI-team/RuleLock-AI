# Cakely + RuleLock contract v2

RuleLock reviews server-calculated order data before payment capture. Cakely calls the backend from a server-side function and never exposes the bearer token to a browser.

## Request

```http
POST /review-order
Authorization: Bearer <RULELOCK_API_TOKEN>
Content-Type: application/json
```

`order_id` is a numeric, stable Cakely order identifier. The idempotency key is `(event_type, order_id)`: retries of a live order return the stored `RULELOCK_REVIEW`; dashboard lab requests set `simulation: true`, use `RULELOCK_SIMULATION`, and do not count in dashboard KPIs.

```json
{
  "order_id": 1001,
  "order_reference": "CK-202610030001",
  "account_id": "customer-42",
  "user_id": 42,
  "session_id": "checkout-session-abc",
  "payment_method": "PREPAID",
  "items": [{"sku":"sku-1","quantity":1,"unit_price":2500}],
  "coupons_applied": ["WELCOME10"],
  "discount_value": 250,
  "subtotal": 2500,
  "total": 2250,
  "account_verified": true,
  "past_orders": 4,
  "past_refusals": 0,
  "session_features": {
    "coupon_attempts_per_session": 1,
    "avg_seconds_between_requests": 12.5,
    "distinct_accounts_same_device": 1,
    "distinct_addresses_same_phone": 1
  }
}
```

Prices, quantities, coupons, and totals must come from Cakely's server-side order and catalog state. Do not trust values from the browser. `order_reference` is an optional human-readable display code; `account_id` is retained in the audit row, so use a pseudonymous identifier where possible.

## Response and payment handling

The response contains `decision`, `reason`, `customer_message`, `payment_action`, `rule_result`, `anomaly_result`, and `enforcement_result`. Decisions are `accept`, `hold`, `reject`, or `void_discount`. Capture payment only for `accept`; for all other decisions, do not capture. Treat timeout, invalid response, and non-2xx responses as `hold`.

1. Create a pending Cakely order with trusted server-calculated values.
2. Call RuleLock before capturing payment.
3. Capture only after `decision=accept`; then mark the order paid after capture succeeds.
4. For `hold`, `reject`, or `void_discount`, follow the returned action and retain the review response on the Cakely order.
5. Log Cakely-side overrides as `RULELOCK_OVERRIDE` in `transaction_events`; the dashboard counts those as manual overrides.

## Dashboard and simulations

The Netlify dashboard requires `DASHBOARD_USER`, `DASHBOARD_PASSWORD`, and `DASHBOARD_SESSION_SECRET`. It authenticates with a short-lived HttpOnly cookie. The dashboard proxy only exposes summary, audit, readiness, pipeline information, and `POST /review-order` with `simulation:true`; it cannot access `/settings/rulelock`.

## Storage and retention

RuleLock stores each review in `transaction_events` and inserts a corresponding immutable row in `rulelock_audit_log`. Apply the SQL files under `data-collection/migrations/` manually to the shared Supabase project. The audit table rejects UPDATE and DELETE. The purge script removes expired `transaction_events` rows after an explicit `--execute`; immutable audit rows remain as a minimal decision record, so do not put customer names, contact information, or raw request payloads there.

Set `RULELOCK_API_TOKEN` on the backend and the same value as a server-side secret in Cakely. Never put it in frontend JavaScript.
