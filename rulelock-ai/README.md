# RuleLock AI

### AI-Powered Business Logic Abuse Detection Platform for Secure E-Commerce Transactions

## What This Project Is About

Sri Lanka CERT has reported a sharp rise in business email compromise and financial cyber-fraud incidents through 2025-2026, with weak governance and low security maturity flagged as contributing factors - including a documented 2026 incident affecting the banking and e-commerce sector. The pattern behind a lot of this seems consistent: local e-commerce and fintech businesses prioritize speed to market over security, and the gaps compound over time.

Most e-commerce platforms enforce rules around payments, discounts, product quantities, and checkout flows. Most security tooling is built to catch technical attacks - SQL injection, XSS, stolen credentials - while business logic vulnerabilities (OWASP's own category for abuse of legitimate functionality) are much harder to catch, because the requests involved are technically valid. An attacker doesn't need to "break in" - they just manipulate parameters and workflows the system already accepts: modifying prices, stacking coupons, tampering with quantities, getting around checkout restrictions.

Sri Lanka adds a wrinkle most global fraud research doesn't cover: it's still a largely cash-based economy where cash-on-delivery is preferred over prepayment, which opens up a whole other attack surface - fake orders and abusive returns/refusals that cost sellers wasted stock, wasted delivery runs, and wasted staff time. A 2020 OWASP-based study of Ghanaian e-commerce platforms found CSRF vulnerabilities in 40% of sites tested and full path disclosure in 53%, but nothing similar has been published for Sri Lankan platforms - and nothing focuses specifically on the business-logic layer rather than the more commonly tested injection/XSS layer.

Most businesses still rely on manual testing and static rules, which don't adapt well to abuse spread thinly across multiple accounts or sessions to stay under any single threshold. That's the gap we're trying to close.

## Our Solution

RuleLock AI sits between the customer and the backend as a detection-and-response layer, combining rule-based validation with ML-based anomaly detection - and, importantly, acting on high-confidence detections automatically instead of just flagging them for someone to review later.

The problem above covers six abuse categories broadly. We've scoped the actual build to three, with the rest documented as future work:

- **Coupon / discount abuse** - our primary demo scenario
- **Price & quantity manipulation** - tampering with checkout parameters
- **COD fake-order & return abuse** - the Sri Lanka-specific angle

## System Components

| # | Component | What it does | Owner |
|---|---|---|---|
| 1 | Transaction Monitoring & Data Collection | Logs product details, quantities, discounts, checkout parameters, session/device IDs, and delivery outcomes for every order | Charuka |
| 2 | Business Rule Validation Engine | Checks transactions against explicit limits - coupon usage, discount ranges, quantity ceilings, minimum purchase, COD order caps, refusal-rate thresholds | Sadini |
| 3 | AI-Based Anomaly Detection | Catches what Component 2 can't by design - abuse spread across accounts/sessions to dodge any single threshold. Isolation Forest / One-Class SVM on session-level features | Nihara |
| 4 | Automated Enforcement Engine | Acts on high-confidence detections without human review - voids discounts, holds COD orders, rate-limits accounts - and logs every action taken | Mishen (Team Lead) |

## Where Machine Learning Actually Fits

Component 3 is the dedicated ML component, but the model doesn't work in isolation - it depends on two other people's work:

- **Charuka's** data collection layer is what makes the model possible in the first place. Every checkout event and coupon attempt gets written to the existing Cakely Supabase database, and she exports a clean sample dataset for Nihara to train and validate the model against.
- **Nihara** owns the model itself - sourcing a public e-commerce dataset as the normal-behaviour baseline, engineering session-level features (request timing, coupon attempts per session, cross-account device/address overlap), training an Isolation Forest (comparing against a One-Class SVM), and wrapping it in a scoring function.
- **Mishen's** enforcement engine is what actually acts on what the model finds - it takes the anomaly score Nihara's model produces, combines it with the rule engine's result, and decides whether to void a discount, hold a COD order, or rate-limit an account.

## Technologies

- **Frontend:** React / HTML, CSS, JavaScript (demo storefront)
- **Backend:** Python (Flask or FastAPI)
- **Database:** Existing Cakely Supabase project
- **Machine Learning:** scikit-learn - Isolation Forest / One-Class SVM
- **Security Testing:** OWASP testing methodology, Burp Suite Community Edition

## CIA Triad Mapping

**Confidentiality** - prevents unauthorised manipulation of transaction and payment-adjacent data.

**Integrity** (core focus) - prices, discounts, and order rules can't be silently bypassed. The enforcement engine blocks violations at the point of attempt, not just after the fact.

**Availability** - repeated fake COD orders and abusive returns eat into real delivery and warehouse capacity. Holding high-risk COD orders for prepayment before dispatch protects that capacity in real time instead of only flagging the loss afterward.

## Team & Component Ownership

- **Mishen (Team Lead)** - Component 4: Automated Enforcement Engine, plus overall integration and coordination across all four components.
- **Charuka** - Component 1: Transaction Monitoring & Data Collection, and the dataset export that feeds the anomaly detection model.
- **Sadini** - Component 2: Business Rule Validation Engine.
- **Nihara** - Component 3: AI-Based Anomaly Detection.

Each person owns one full component end-to-end - design, implementation, testing, and documentation - so the workload stays evenly split, with Mishen carrying the extra (but standard) leadership job of tying all four pieces together.

## Timeline

| Month | Focus |
|---|---|
| July | Topic finalized, requirements gathering, environment and repo setup |
| August | Database schema design, rule engine skeleton, dataset research for the ML model |
| September | Core build - checkout API, rule checks, first version of the anomaly detection model |
| October | Feature pipeline connected end-to-end, enforcement engine integration |
| **November** | **Demo - full pipeline running end-to-end** |
| December | Refinement from demo feedback, final testing, documentation, final report |

## Getting Started

```bash
docker-compose up --build
```

| Service | Port |
|---|---|
| data-collection | 5001 |
| rule-engine | 5002 |
| anomaly-detection | 5003 |
| enforcement-engine | 5004 |

Each component also runs and tests independently - see the README inside its own folder.

## License

MIT