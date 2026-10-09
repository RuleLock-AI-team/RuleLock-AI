# RuleLock AI backend

The deployed service is the Flask app in this directory. Rule checks, anomaly scoring, and enforcement run in-process. The sibling `rule-engine/`, `anomaly-detection/`, and `enforcement-engine/` folders are legacy implementations and are not deployed.

## Contract

Cakely calls `POST /review-order` with `Authorization: Bearer <RULELOCK_API_TOKEN>` and server-calculated order values. `order_id` must be numeric and stable. Responses use `accept`, `hold`, `reject`, or `void_discount`; Cakely captures payment only for `accept` and treats timeout or error as `hold`.

Normal requests write `RULELOCK_REVIEW`; requests with `simulation:true` write `RULELOCK_SIMULATION`. Both are idempotent by event type and order ID, but simulations are excluded from dashboard metrics. A PostgREST database function writes each transaction event and its minimal immutable `rulelock_audit_log` row atomically. Cakely owns checkout and `RULELOCK_OVERRIDE` events.

## Security and operations

Production startup requires `RULELOCK_API_TOKEN`. `RULELOCK_ALLOW_NO_AUTH=1` is only for local development. The dashboard proxy requires `DASHBOARD_USER`, `DASHBOARD_PASSWORD`, and `DASHBOARD_SESSION_SECRET` in Netlify and keeps the backend token server-side.

`/health` is fast liveness. `/ready` checks that the model is loaded and Supabase is reachable. `/pipeline/info` reports the active model thresholds, configured rule thresholds, and model feature names.

## Retention and audit privacy

`scripts/purge_old_events.py` uses `RETENTION_DAYS` (default `365`), reports the expired transaction-event count by default, and only deletes with `--execute`. Apply the database migrations manually. `rulelock_audit_log` is insert-only and is excluded from event purging; keep its rows minimal and do not store names, contact information, or raw request payloads. See [docs/architecture.md](../docs/architecture.md) for the retention policy.

## Migrations

Apply these SQL files manually to the shared Supabase database, in order:

1. `migrations/2026-10-03_rulelock_review_idempotency.sql` enforces one live review and one simulation row per order.
2. `migrations/2026-10-03_rulelock_audit_log.sql` creates the immutable audit table and its indexes/triggers.

This repository change does not run SQL against Supabase. Configure `SUPABASE_URL` and `SUPABASE_SECRET_KEY` in the backend environment.

## Model

Model inputs are clipped to the training ranges in `features.py`; training and evaluation are synthetic and circular, not evidence of real-world detection accuracy. Run `python train_model.py`, `python evaluate.py`, or `pytest` from this directory as needed.
