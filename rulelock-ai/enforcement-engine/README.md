# Component 4 — Automated Enforcement Engine
**Owner: Mishen (team leader) — also owns overall integration**

The decision-and-action layer. Consumes rule-engine's and
anomaly-detection's outputs and automatically voids discounts, holds
COD orders for prepayment, or rate-limits accounts — no human review
in the loop for high-confidence detections.

## Run locally
```bash
pip install -r requirements.txt
python app.py        # http://localhost:5004
pytest
```

## What's implemented
- `decide()` — the full decision tree, tested for all four outcomes
- `actions.py` — simulated void/hold/rate-limit actions
- `audit_log.py` — append-only log (SQLite locally, Postgres in the integrated demo)
- `POST /enforce` and `GET /audit-log` endpoints

## What to build here (the real coursework / integration role)
- Agree the internal API contract (JSON shape each component sends/returns) with the other three
- Wire `/enforce` into `data-collection`'s `/checkout`, called after rule-engine and anomaly-detection
- Point `AUDIT_LOG_PATH` logic at the shared Postgres `audit_log` table for the real demo
- End-to-end integration testing across all four components
- Sharpen `decide()` beyond one-signal-triggers-one-action, per the TODO in `decision.py`
