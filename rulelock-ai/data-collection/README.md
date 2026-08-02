# Component 1 — Transaction Monitoring & Data Collection
**Owner: Charuka**

The demo storefront's checkout API — browse, cart, apply-coupon, checkout —
plus (once wired in) writing every event to Postgres so Components 2-4
have real data to work against.

## Run locally
```bash
pip install -r requirements.txt
python app.py        # http://localhost:5001
```

## What's implemented
- Working `/browse`, `/cart`, `/apply-coupon`, `/checkout` endpoints
- A minimal static storefront frontend at `/`
- `schema.sql` — the full Postgres schema for the project

## What to build here (the real coursework)
- Wire `db.py` into every route so events are actually persisted
- Session/device-id capture middleware
- Call rule-engine → anomaly-detection → enforcement-engine, in order, from `/checkout`
