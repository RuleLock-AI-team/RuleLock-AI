# Architecture

## Request flow

1. Client calls `data-collection` to build a cart and apply a coupon.
2. Before confirming checkout, `data-collection` calls `rule-engine`'s `POST /validate`.
3. `data-collection` calls `anomaly-detection`'s `POST /score` for the session.
4. Both results go to `enforcement-engine`'s `POST /enforce`, which decides
   and acts — void discount, hold COD order, or rate-limit the account —
   and writes an audit log entry before responding.
5. Every automated action is queryable via `enforcement-engine`'s `GET /audit-log`.

## Why this isn't a "human error" project

No step above depends on a person reading a warning and deciding what
to do. The vulnerability (business logic that accepts technically valid
but abusive requests) and the control (automatic rule + ML detection,
automatic action) are both technical, end to end.

## CIA mapping

- **Confidentiality** — `enforcement-engine`, `rule-engine` (prevents unauthorised manipulation of transaction/payment data)
- **Integrity** (core focus) — all four components; `enforcement-engine` blocks at the point of attempt
- **Availability** — `enforcement-engine`'s COD-hold action, protecting delivery/warehouse capacity in real time

## Threat model

| Attack | Caught by | Status |
|---|---|---|
| Coupon stacking / limit abuse | rule-engine | TODO |
| Price/quantity tampering | rule-engine | partially implemented (quantity ceiling) |
| Abuse spread across accounts/sessions | anomaly-detection | implemented (synthetic data) |
| COD fake-order / high refusal rate | rule-engine | TODO |
| Any of the above at high confidence | enforcement-engine | implemented (decision logic + tests) |
