# RuleLock AI

**AI-Powered Business Logic Abuse Detection Platform for Secure E-Commerce Transactions**

*Finalized project proposal — approved by the module coordinator.*

## Problem

E-commerce platforms enforce business rules around payments, discounts,
quantities, and checkout workflows. Most security tooling targets
traditional technical attacks — SQL injection, XSS, credential theft —
while business logic vulnerabilities (OWASP's category for abuse of
legitimate functionality) remain much harder to detect, because the
requests involved are technically valid. Sri Lanka's cash-on-delivery-
heavy e-commerce market adds a locally distinct attack surface most
global fraud research doesn't cover: fake-order placement and abusive
returns/refusals.

## Solution

A security layer between customers and the application backend,
combining rule-based validation with ML-based anomaly detection — and,
critically, **acting on high-confidence detections automatically**
rather than only surfacing them for manual review.

**Scoped to three abuse categories** (of six identified in the full
problem framing — the rest are documented as future work):
- Coupon / discount abuse — the primary demo scenario
- Price & quantity manipulation — parameter tampering on checkout requests
- COD fake-order & return abuse — the Sri Lanka-specific angle

## Architecture

```
client → data-collection (storefront + checkout API)
              │
              ├─→ rule-engine          (explicit rule validation)
              │
              └─→ anomaly-detection    (Isolation Forest / One-Class SVM)
                              │
                              ▼
                     enforcement-engine  (decides + acts + logs)
                              │
                              ▼
                          audit_log (Postgres)
```

## Components & owners

| # | Component | Folder | Owner |
|---|---|---|---|
| 1 | Transaction Monitoring & Data Collection | `data-collection/` | Charuka |
| 2 | Business Rule Validation Engine | `rule-engine/` | Sadini |
| 3 | AI-Based Anomaly Detection | `anomaly-detection/` | Nihara |
| 4 | Automated Enforcement Engine + integration | `enforcement-engine/` | Mishen (leader) |

Each member owns one full component end-to-end — design, implementation,
testing, documentation. Mishen additionally owns cross-component
integration.

## CIA mapping

- **Confidentiality** — prevents unauthorised manipulation of transaction and payment-adjacent data.
- **Integrity** (core focus) — prices, discounts, and order rules can't be silently bypassed; the enforcement engine blocks violations at the point of attempt.
- **Availability** — repeated fake COD orders consume real delivery/warehouse capacity; holding high-risk COD orders for prepayment before dispatch protects operational availability in real time.

## Technologies

- Frontend: HTML/CSS/JS demo storefront (`data-collection/static/`)
- Backend: Python (Flask)
- Database: PostgreSQL (`data-collection/schema.sql`)
- Machine learning: scikit-learn — Isolation Forest / One-Class SVM (`anomaly-detection/`)
- Security testing: OWASP methodology, Burp Suite Community Edition

## Getting started

Each service runs independently for local development — see each
component's own README. To bring up the full stack together:

```bash
docker-compose up --build
```

| Service | Port |
|---|---|
| postgres | 5432 |
| data-collection | 5001 |
| rule-engine | 5002 |
| anomaly-detection | 5003 |
| enforcement-engine | 5004 |

## Deadlines

- Proposal submission — 9 Aug 2026 *(done — approved)*
- Software stack & progress — 6 Sep 2026
- Final report — 27 Sep 2026

## License

MIT — see `LICENSE`.
