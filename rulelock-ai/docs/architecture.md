# Architecture and threat model

## Deployed request flow

Cakely sends trusted order data to `POST /review-order` before payment capture, authenticated by `RULELOCK_API_TOKEN`. The Flask backend in `data-collection/` runs rule validation, anomaly scoring, and enforcement in-process. It writes one `RULELOCK_REVIEW` event for a live order or `RULELOCK_SIMULATION` for the lab, keyed idempotently by event type and numeric order ID. Simulations are excluded from dashboard KPIs.

Each review also gets a minimal row in `rulelock_audit_log`. A PostgREST RPC writes the transaction event and audit row in one database transaction. The table is insert-only: a PostgreSQL trigger rejects UPDATE and DELETE. Dashboard search, action filtering, and cursor pagination are pushed into Supabase queries before LIMIT. Dashboard blocked-threat delta compares the last 24 hours with the preceding 24 hours; `RULELOCK_OVERRIDE` counts come from Cakely transaction events.

Cakely owns checkout, coupon, applied-decision, and override events, including session/device/account and hashed phone/address metadata. The Netlify dashboard requires username/password login and a four-hour HMAC-signed HttpOnly cookie. Its proxy forwards authenticated summary, audit, readiness, pipeline info, and simulation-only review calls. It does not expose `/settings/rulelock`.

## Threat-model status

| Threat | Status | Control and limit |
|---|---|---|
| Browser changes price, quantity, discount, or payment parameters | Mitigated at the review boundary | Cakely must submit server-calculated order/catalog values; RuleLock checks configured limits and catalog prices. |
| Coupon stacking and configured rule violations | Mitigated | Deterministic rules run before payment capture. Cakely must hold payment for every non-accept response. |
| Cross-account/session abuse | Partially mitigated | Isolation Forest uses session and cross-account features. Training and evaluation remain synthetic and circular; real-world detection quality is unproven. |
| Unauthorized backend review calls | Mitigated when configured | Production refuses to start without `RULELOCK_API_TOKEN`. Local no-auth mode requires explicit `RULELOCK_ALLOW_NO_AUTH=1`. |
| Unauthorized dashboard access | Mitigated when configured | Netlify login issues a short-lived signed HttpOnly cookie; proxy calls require it and upstream credentials stay server-side. |
| Audit row alteration | Mitigated for row UPDATE/DELETE | Database trigger rejects both. Database owners can still alter schema or disable triggers; apply migrations and tightly restrict Supabase service credentials. |
| Database/model outage | Fail closed | `/ready` reports model and Supabase checks; review pipeline returns hold when required dependencies fail. `/health` remains a fast liveness check. |
| Audit retention and privacy | Partially mitigated | `transaction_events` default to 365 days and the purge is operator-triggered. Immutable audit rows remain without customer names or raw payloads; use pseudonymous account IDs. |

The `rule-engine/`, `anomaly-detection/`, and `enforcement-engine/` directories are retained legacy copies and are not deployed.

## Operations and retention

`scripts/purge_old_events.py` uses `RETENTION_DAYS` (default `365`), performs a dry run by default, and deletes only with `--execute`. It removes expired `transaction_events`; immutable `rulelock_audit_log` rows are retained. Apply migrations manually; repository changes do not run SQL against Supabase.

## Detection limits

The deployed Isolation Forest is trained on synthetic sessions. Evaluation compares it with a One-Class SVM on generated data and authored fixtures, so the measurements are circular and do not establish real-world precision, recall, or false-positive rates. A representative e-commerce dataset and independently labeled outcomes are needed before claiming production detection quality.
