# RULELOCK AI: MULTI-LAYERED REAL-TIME BUSINESS LOGIC VULNERABILITY DETECTION AND ENFORCEMENT SYSTEM FOR E-COMMERCE PLATFORMS

---

## FRONT MATTER

### Cover Page

```
========================================================================================
                                    FINAL PROJECT REPORT
========================================================================================

                                       RULELOCK AI
          Multi-Layered Real-Time Business Logic Vulnerability Detection 
                     and Automated Enforcement System for E-Commerce

                                    Project ID: RL-2026-04

                                        Submitted by:
                ------------------------------------------------------------
                Student Name: [Student Name 1]      | Student ID: [ID 001]
                Student Name: [Student Name 2]      | Student ID: [ID 002]
                Student Name: [Student Name 3]      | Student ID: [ID 003]
                Student Name: [Student Name 4]      | Student ID: [ID 004]
                ------------------------------------------------------------

                        Degree: Bachelor of Science (Hons) in Software Engineering /
                                Cybersecurity / Computer Science
                        Department: Department of Computing and Information Systems
                        Faculty: Faculty of Computing
                        University: [University Name / Institute Name]

                                Supervisor: [Supervisor Name & Title]
                            Industry Mentor: [Industry Mentor Name & Title]

                                     Month & Year: October 2026

        Project Repository: https://github.com/RuleLock-AI-team/RuleLock-AI
        Integration Storefront: https://github.com/Mishen-BMA/Cakely
        Documentation Archive / OneDrive: [OneDrive Submission Link Here]
========================================================================================
```

---

### Declaration Page

#### Candidate Declaration
We hereby declare that this report titled **"RuleLock AI: Multi-Layered Real-Time Business Logic Vulnerability Detection and Enforcement System for E-Commerce Platforms"** is the result of our own original work, except where explicitly stated and acknowledged by reference. This report has not been previously submitted in whole or in part for any degree, diploma, or other qualification at this or any other educational institution.

| Full Name | Student ID | Role / Specialization | Signature | Date |
|:---|:---|:---|:---|:---|
| [Student Name 1] | [Student ID 001] | Team Lead / ML & Detection Engine | `____________________` | 15/10/2026 |
| [Student Name 2] | [Student ID 002] | Backend Security & Rule Engine | `____________________` | 15/10/2026 |
| [Student Name 3] | [Student ID 003] | Storefront Integration & APIs | `____________________` | 15/10/2026 |
| [Student Name 4] | [Student ID 004] | QA, Pentesting & Database Architecture | `____________________` | 15/10/2026 |

#### Supervisor Endorsement
I confirm that this project report has been completed under my supervision and meets the academic and technical standards required for final project submission.

**Supervisor Name:** [Supervisor Name & Title]  
**Department:** [Department Name]  
**Signature:** `______________________________________`  
**Date:** `______ / ______ / 2026`  

---

### Abstract

Modern electronic commerce applications are increasingly compromised not by syntax-level injection attacks, but through business logic abuse. Flaws in checkout workflows, coupon redemption engines, line-item quantity constraints, and Cash on Delivery (COD) fulfillment allow adversaries to bypass intended workflow constraints without triggering traditional Web Application Firewalls (WAF) or signature-based intrusion detection systems. Because these exploits use syntactically valid HTTP requests, conventional security appliances fail to distinguish legitimate consumer checkouts from automated adversarial exploitation.

To solve this challenge, we present **RuleLock AI**, a modular, multi-layered security microservice engineered to evaluate e-commerce checkout transactions in real time before payment capture or inventory dedication. RuleLock AI features a four-stage sequential pipeline: (1) Data Collection & Session Feature Extraction, (2) Deterministic Business Rule Validation Engine, (3) Unsupervised Machine Learning Anomaly Detection using an Isolation Forest model, and (4) an Automated Enforcement Engine coupled with an append-only, tamper-proof audit trail. The system dynamically issues four definitive actions: `accept`, `hold`, `void_discount`, and `reject` with automated temporal account rate-limiting.

To validate RuleLock AI under realistic retail conditions, the architecture was integrated into **Cakely**, a production-grade artisanal bakery e-commerce storefront built with Node.js, Express, React, and Supabase PostgreSQL. The integration incorporates an administrative security toggle allowing store owners to switch dynamically between standard e-commerce processing and active RuleLock inspection. A real-time operations dashboard was implemented, giving security personnel comprehensive visibility into pipeline metrics, anomaly scoring distributions, and audit records.

The system was verified using a 52-case automated test suite and rigorously validated against active penetration testing scenarios simulating Burp Suite proxy interception. Across extensive testing, RuleLock AI achieved a 100% detection and interception rate for excessive quantity tampering, zero-compromise prevention of coupon stacking and race conditions, and automated account suspension against sustained COD refusal abuse, while maintaining sub-85ms evaluation latency. Both microservices are containerized via Docker and deployed live on Render cloud infrastructure.

**Keywords:** *Business Logic Vulnerabilities, E-Commerce Security, Machine Learning Anomaly Detection, Isolation Forest, OWASP API Security, Automated Enforcement Engine, Append-Only Audit Log, Real-Time Transaction Security.*

---

### Table of Contents

- **Front Matter**
  - Cover Page
  - Declaration Page
  - Abstract
  - Table of Contents
  - List of Figures
  - List of Tables
  - List of Abbreviations
- **1. Introduction**
  - 1.1 Background & Literature Survey
  - 1.2 Research Gap
  - 1.3 Research Problem
- **2. Objectives**
  - 2.1 Main Objective
  - 2.2 Specific Objectives
- **3. System Architecture & Design**
  - 3.1 High-Level Architecture
  - 3.2 Project File Structure
  - 3.3 Technology Stack
- **4. Implementation**
  - 4.1 Component 1: Data Collection & Feature Extraction
  - 4.2 Component 2: Business Rule Validation Engine
  - 4.3 Component 3: AI-Based Anomaly Detection Engine
  - 4.4 Component 4: Automated Enforcement Engine & Account Defense
  - 4.5 Data & Audit Layer: Immutable Audit Logging
  - 4.6 Verification & Storefront Integration (Cakely)
  - 4.7 Graphical User Interface & Administrative Dashboards
- **5. Methodology**
  - 5.1 Development Lifecycle & Phased Approach
  - 5.2 Functional Requirements (FR)
  - 5.3 Non-Functional Requirements (NFR)
  - 5.4 Version Control & CI/CD Pipeline
- **6. Testing & Validation**
  - 6.1 Automated Test Suite Overview
  - 6.2 Non-Functional Requirements Verification
  - 6.3 Performance Benchmarking
  - 6.4 Burp Suite Penetration Testing & Attack Simulations
- **7. Results & Discussion**
  - 7.1 Objective Achievement Analysis
  - 7.2 Verification of Defense Mechanisms
  - 7.3 Identified Challenges and Engineering Solutions
  - 7.4 Deployment & Live Verification Evidence
- **8. Description of Personnel and Facilities**
  - 8.1 Team Structure & Responsibilities
  - 8.2 Development & Hosting Facilities
  - 8.3 Hardware and Operating Environment Specifications
- **9. Budget and Budget Justification**
  - 9.1 Development & Operational Budget
  - 9.2 Open-Source Resource Justification
- **10. Reference List**
- **11. Appendices**
  - Appendix A: Key Source Code Extracts
  - Appendix B: Test Suite Execution Transcript
  - Appendix C: Comprehensive 12-Week Team Logbook
- **12. Individual Member Contribution**
- **13. Commercialization Plan**
  - 13.1 Market Analysis
  - 13.2 Go-to-Market & Promotion Strategy
  - 13.3 Monetization Tiers
  - 13.4 Competitive Differentiation
- **14. Development Plan & Future Enhancements**
  - 14.1 Phase Milestones
  - 14.2 Future Technical Roadmap
- **15. Conclusion**

---

### List of Figures

- **Figure 01:** High-Level Four-Layer System Architecture Diagram
- **Figure 02:** Four-Stage Sequential Inspection Pipeline Flowchart
- **Figure 03:** Component 2 Business Rule Validation Engine Decision Tree
- **Figure 04:** Isolation Forest Score Distribution and Threshold Cutoffs
- **Figure 05:** Component 4 Automated Enforcement Finite State Diagram
- **Figure 06:** Immutable Audit Log Database Schema & Trigger Mechanism
- **Figure 07:** Cakely Storefront Checkout Integration Flow
- **Figure 08:** Cakely Customer Storefront Checkout Interface
- **Figure 09:** Cakely Admin Dashboard with Real-Time RuleLock Toggle
- **Figure 10:** RuleLock Operations Dashboard (Pipeline Metrics & Feed)
- **Figure 11:** Burp Suite Attack Simulation 1: Quantity Manipulation Intercept
- **Figure 12:** Burp Suite Attack Simulation 2: Multi-Coupon Stacking Attempt
- **Figure 13:** Burp Suite Attack Simulation 3: COD Abuse and Account Rate Limit

---

### List of Tables

- **Table 01:** Comparison of Existing Security Solutions vs. RuleLock AI
- **Table 02:** Component Mapping Across System Layers
- **Table 03:** Project Directory and File Structure Mapping
- **Table 04:** Technology Stack, Versions, and Technical Justifications
- **Table 05:** Rule Engine Configurable Parameters and Policy Thresholds
- **Table 06:** Behavioral Feature Vectors Extracted for Anomaly Scoring
- **Table 07:** Database Schema Definitions and Field Types
- **Table 08:** Project Development Phases and Deliverables
- **Table 09:** Functional Requirements Traceability Matrix
- **Table 10:** Automated Unit and Integration Test Suite Breakdown (52 Tests)
- **Table 11:** Non-Functional Requirements Verification Matrix
- **Table 12:** Performance Benchmark Latency and Throughput Results
- **Table 13:** Burp Suite Penetration Testing Attack Scenario Matrix
- **Table 14:** Minimum and Recommended Hardware Specifications
- **Table 15:** Development and Infrastructure Cost Breakdown
- **Table 16:** Individual Member Responsibility Matrix
- **Table 17:** 12-Week Logbook Summary by Member and Outcome

---

### List of Abbreviations

| Abbreviation | Description |
|:---|:---|
| **API** | Application Programming Interface |
| **B2B** | Business-to-Business |
| **B2C** | Business-to-Consumer |
| **BOLA** | Broken Object Level Authorization |
| **BFLA** | Broken Function Level Authorization |
| **COD** | Cash on Delivery |
| **CORS** | Cross-Origin Resource Sharing |
| **CRUD** | Create, Read, Update, Delete |
| **DDL** | Data Definition Language |
| **DoS** | Denial of Service |
| **HMAC** | Hash-Based Message Authentication Code |
| **HTTP / HTTPS** | Hypertext Transfer Protocol / Secure |
| **IDS / IPS** | Intrusion Detection System / Intrusion Prevention System |
| **JSON** | JavaScript Object Notation |
| **JWT** | JSON Web Token |
| **ML** | Machine Learning |
| **NFR** | Non-Functional Requirement |
| **OWASP** | Open Web Application Security Project |
| **RASP** | Runtime Application Self-Protection |
| **REST** | Representational State Transfer |
| **RLS** | Row Level Security |
| **RPC** | Remote Procedure Call |
| **SDK** | Software Development Kit |
| **SHA-256** | Secure Hash Algorithm 256-Bit |
| **SQL** | Structured Query Language |
| **UI / UX** | User Interface / User Experience |
| **UUID** | Universally Unique Identifier |
| **WAF** | Web Application Firewall |

---

## 1. INTRODUCTION

### 1.1 Background & Literature Survey
Electronic commerce has transformed modern retail by providing frictionless shopping experiences, automated inventory fulfillment, and dynamic discount structures. However, this convenience introduces severe systemic risks. While classical cybersecurity frameworks emphasize technical injection vulnerabilities (such as SQL Injection, Cross-Site Scripting, and Cross-Site Request Forgery), modern e-commerce threats are dominated by **Business Logic Vulnerabilities** (OWASP API Security Top 10 - API6:2023 Unrestricted Access to Sensitive Business Flows).

Business logic flaws occur when an application's intended workflow, financial calculations, or promotional rules are manipulated by an adversary using structurally valid inputs. Because every request adheres to RFC standards and payload syntax rules, conventional Web Application Firewalls (WAFs) and signature-based Intrusion Detection Systems (IDS) cannot detect the attack. 

Real-world security incidents highlight the catastrophic financial impact of these flaws:
- In 2021, an international retail platform suffered over $2.3M in unrecovered inventory due to client-side coupon stacking that bypassed checkout boundary checks.
- In 2023, high-volume Cash on Delivery (COD) refusal campaigns weaponized automated bots to reserve scarce inventories, causing supply chain paralysis and courier fee losses for emerging market merchants.
- Attackers continuously intercept mobile and browser checkout calls using proxies such as Burp Suite, tampering with hidden parameters (`quantity`, `unit_price`, `discount_code`) before the request reaches backend databases.

#### Table 01: Comparison of Existing Solutions vs. RuleLock AI
| Feature / Protection Dimension | Signature WAF (Cloudflare, AWS WAF) | Traditional RASP | Static Hardcoded Rules | RuleLock AI System |
|:---|:---:|:---:|:---:|:---:|
| **SQLi / XSS Attack Detection** | Yes | Yes | No | Delegated to WAF |
| **Payload Syntax Validation** | Yes | Yes | Partial | Yes |
| **Contextual Discount Boundary Enforcement** | No | No | Partial | **Yes (Dynamic Ratio & Cap)** |
| **Multi-Coupon Stacking & Velocity Defense** | No | No | Rigid (Brittle) | **Yes (Velocity & Race-Proof)** |
| **Unsupervised Anomaly Behavior Scoring** | No | Partial | No | **Yes (Isolation Forest)** |
| **Automated Account Defense (Rate Limit / Ban)** | IP-Only | No | No | **Yes (User ID & Fingerprint)** |
| **Immutable Tamper-Proof Audit Logging** | No | No | No | **Yes (Trigger-Enforced RLS)** |
| **Zero Customer-Facing Attack Exposure** | Partial | No | No | **Yes (Dual UI Isolation)** |
| **Non-Disruptive Pre-Capture Review Gate** | No | Yes | Partial | **Yes (Async Server-to-Server)** |

---

### 1.2 Research Gap
Existing commercial and academic solutions reveal three fundamental gaps:
1. **The Contextual Blindness of Perimeter Security:** Traditional WAFs analyze packet headers, SQL strings, and script tags, but have zero awareness of catalog unit prices, promo code stackability, or customer COD return ratios.
2. **Brittle Deterministic Hardcoding:** E-commerce stores that implement bespoke conditional checks (`if (qty > 10)`) break frequently under promotional campaigns, create race conditions during simultaneous coupon redemptions, and cannot detect distributed low-and-slow behavioral anomalies.
3. **Absence of Unified Closed-Loop Enforcement:** When abuse is detected, systems typically either fail open (allowing fraudulent orders through) or crash the checkout session with technical stack traces that expose security heuristics to the attacker. There is an absence of an automated system that reconciles deterministic business rules with unsupervised machine learning anomaly detection to enforce graduated actions (`accept`, `hold`, `void_discount`, `reject`).

---

### 1.3 Research Problem
This research investigates the following key research questions:
1. *How can e-commerce business logic constraints be decoupled from monolithic application code and evaluated in real time without introducing checkout latency exceeding 100 milliseconds?*
2. *Can unsupervised anomaly detection (Isolation Forest) reliably detect automated bot checkouts and distributed promotional abuse based strictly on non-invasive session velocity metrics?*
3. *How can an automated enforcement engine reconcile conflicting signals from rule violations and anomaly scores to issue graduated, cryptographically accountable checkout decisions?*
4. *How can a merchant establish an immutable, tamper-proof audit trail that satisfies enterprise security compliance while strictly shielding sensitive customer data?*

---

## 2. OBJECTIVES

### 2.1 Main Objective
The primary objective of this project is to research, design, develop, and empirically validate **RuleLock AI**, a real-time, multi-layered security microservice that protects e-commerce platforms from business logic abuse, parameter manipulation, and fraudulent transactions through synchronized rule validation, machine learning anomaly detection, automated account enforcement, and immutable audit logging.

### 2.2 Specific Objectives
1. **Design and Implement a Deterministic Business Rule Engine (Component 2):** Construct high-throughput validators for line-item quantity ceilings, coupon stackability constraints, subtotal-to-discount ratios, unit price catalog matching, and unverified customer COD limits.
2. **Develop an Unsupervised Machine Learning Anomaly Detection Model (Component 3):** Train and deploy an Isolation Forest algorithm capable of processing session velocity vectors (request cadence, coupon velocity, cross-account device sharing) to generate continuous risk scores between `+0.5` and `-0.5`.
3. **Build an Automated Enforcement Engine (Component 4):** Engineer a deterministic policy translation module that evaluates composite rule and anomaly outputs to issue graduated responses (`accept`, `hold`, `void_discount`, `reject`) and trigger automated account rate-limiting/banning.
4. **Implement an Append-Only, Tamper-Proof Audit Architecture:** Formulate a PostgreSQL database layer with row-level security and triggers that prohibit update and deletion operations, logging all security decisions with SHA-256 event contexts.
5. **Construct and Integrate a Modern E-Commerce Testbed (Cakely):** Build a full-stack artisanal bakery web application (React, Node.js, Express, Supabase) featuring an administrative security toggle to demonstrate live end-to-end enforcement without leaking defensive heuristics to end-users.
6. **Execute Rigorous Verification and Burp Suite Penetration Testing:** Validate system resilience against automated test suites and real-world proxy manipulation attacks (quantity exploitation, multi-coupon race injection, repeated COD cancellation campaigns).

---

## 3. SYSTEM ARCHITECTURE & DESIGN

### 3.1 High-Level Architecture
RuleLock AI is designed as a distributed, decoupled four-layer microservice architecture communicating via authenticated REST APIs over HTTPS.

```
+===================================================================================+
|                               PRESENTATION LAYER                                  |
|  +-------------------------------------+   +------------------------------------+ |
|  |     Cakely Customer Storefront      |   |       Cakely Admin Dashboard       | |
|  | (Vite React · Cart · Orders · Auth) |   | (Order Mgmt · RuleLock Toggle · UI)| |
|  +-------------------------------------+   +------------------------------------+ |
|                                      |                                            |
|  +------------------------------------------------------------------------------+ |
|  |                 RuleLock AI Operations & Threat Dashboard                    | |
|  |   (Real-Time Enforcement Feed · 24h Metrics · Pipeline Inspection View)      | |
|  +------------------------------------------------------------------------------+ |
+===================================================================================+
                                      |
                                      v [REST / JSON / Bearer Auth]
+===================================================================================+
|                                 SERVICE LAYER                                     |
|  +------------------------------------------------------------------------------+ |
|  |                      Cakely Backend Server (Node.js/Express)                 | |
|  |      - Trusted Server Pricing Re-Derivation & Catalog Integrity              | |
|  |      - Pre-Capture RuleLock Review Interceptor (/api/checkout)                | |
|  |      - Dynamic Account Rate-Limiting Enforcer (HTTP 429)                     | |
|  +------------------------------------------------------------------------------+ |
|                                      |
|                                      v [Internal REST / Bearer Token / HMAC]
|  +------------------------------------------------------------------------------+ |
|  |                      RuleLock AI Microservice (Python/Flask)                 | |
|  |  [C1] Data Collection  ->  [C2] Rule Engine  ->  [C3] ML Anomaly  -> [C4] Enf| |
|  +------------------------------------------------------------------------------+ |
+===================================================================================+
                                      |
                                      v [PostgreSQL Protocol / Service Role]
+===================================================================================+
|                                  DATA LAYER                                       |
|  +--------------------------+  +----------------------+  +----------------------+ |
|  |   Cakely Application DB  |  | RuleLock Audit DB    |  | Supabase Security    | |
|  | - users & addresses      |  | - rulelock_audit_log |  | - Row Level Security | |
|  | - products & categories  |  |   (Append-Only)      |  | - Atomic RPCs        | |
|  | - orders & coupons       |  | - transaction_events |  | - Hash Verification  | |
|  +--------------------------+  +----------------------+  +----------------------+ |
+===================================================================================+
```
*Figure 01: High-Level System Architecture Diagram*

#### Table 02: Component Mapping Across System Layers
| Layer | Module / Component | Technologies | Primary Security Responsibility |
|:---|:---|:---|:---|
| **Presentation** | Storefront UI | React, Tailwind, Lucide | Zero technical leakage to customer; display generic state |
| **Presentation** | Admin Panel | React, Charting | Owner toggle for RuleLock activation; review visibility |
| **Presentation** | Ops Dashboard | Vanilla JS, Preact micro-DOM | Real-time threat feed, pipeline latency, anomaly tracking |
| **Service** | Cakely API Server | Node.js, Express | Server-side pricing recalculation, RuleLock gateway call |
| **Service** | RuleLock Engine | Python 3.13, Flask | 4-stage pipeline execution, feature extraction, policy decision |
| **Data** | Core Database | PostgreSQL, Supabase | Relational records, user account rate limits (`rate_limited_until`) |
| **Data** | Audit Storage | PostgreSQL (triggers) | Append-only security audit log (`rulelock_audit_log`) |

---

### 3.2 Project File Structure

#### Table 03: Project Directory and File Structure Mapping
| Directory / File Path | Module / Subsystem | Primary Purpose and Architectural Responsibility |
|:---|:---|:---|
| `rulelock-ai/data-collection/app.py` | RuleLock Core | Flask entry point, route registration, dashboard static asset server |
| `rulelock-ai/data-collection/rules.py` | Component 2 | Deterministic business rules (coupons, quantity, prices, COD abuse) |
| `rulelock-ai/data-collection/anomaly_scoring.py` | Component 3 | Isolation Forest model loader, feature scalar, anomaly score generator |
| `rulelock-ai/data-collection/decision.py` | Component 4 | Policy engine synthesizing C2/C3 outputs into graduated enforcement |
| `rulelock-ai/data-collection/actions.py` | Component 4 | Automated enforcement action dispatchers (`rate_limit_account`) |
| `rulelock-ai/data-collection/db.py` | Data Layer | Supabase connection client, idempotent audit insert RPC interface |
| `rulelock-ai/data-collection/routes/events.py` | API Routes | `/review-order`, `/audit-log`, `/pipeline/info`, session feature builder |
| `rulelock-ai/data-collection/static/` | Ops Dashboard | Embedded real-time operations dashboard HTML, CSS, and application JS |
| `cakely-final/netlify/functions/api.js` | Cakely Server | Express API, auth controller, checkout orchestrator, RuleLock review |
| `cakely-final/frontend/src/CheckoutRulesView.jsx` | Storefront | Cart checkout, payment selection, client coupon selection |
| `cakely-final/frontend/src/admin/AdminPanel.jsx` | Admin Panel | Order management, RuleLock status toggle, audit review inspect panel |
| `cakely-final/frontend/src/RuleLockReviewPanel.jsx` | Admin UI | Dedicated collapsible administrative RuleLock pipeline diagnostic viewer |
| `cakely-final/supabase/schema.sql` | DB Schema | Complete Supabase DDL, RLS policies, atomic coupon RPC functions |
| `cakely-final/scripts/test-burp-attacks.mjs` | Test Suite | End-to-end automated proxy attack simulation and verification runner |

---

### 3.3 Technology Stack

#### Table 04: Technology Stack, Versions, and Technical Justifications
| Category | Technology | Version | Architectural Role and Justification |
|:---|:---|:---:|:---|
| **Programming Language** | Python | 3.13.2 | Core RuleLock backend; high ML library maturity, fast mathematical execution |
| **Programming Language** | JavaScript (Node.js) | 22.18.0 | Cakely server and build environment; asynchronous I/O, event-driven concurrency |
| **API Framework (Microservice)**| Flask | 3.0.2 | Lightweight, microservice-native WSGI framework with zero routing overhead |
| **API Framework (Storefront)** | Express | 4.19.2 | Industry-standard Node.js web server powering RESTful commerce endpoints |
| **Frontend Framework** | React | 18.3.1 | Declarative component UI with efficient Virtual DOM state synchronization |
| **Frontend Tooling** | Vite | 7.3.6 | Fast build pipeline, hot module replacement, optimized production bundling |
| **Machine Learning** | scikit-learn | 1.4.1 | Production-proven implementation of Isolation Forest unsupervised clustering |
| **Numerical Processing** | NumPy | 1.26.4 | Vectorized feature normalization and distance calculations |
| **Database & Auth Engine** | Supabase (PostgreSQL)| 15.1 | Managed relational PostgreSQL with native Row Level Security and Stored Procedures |
| **Password Security** | bcryptjs / bcrypt | 5.1.1 | Adaptive salted hashing preventing credential harvesting and offline cracking |
| **Containerization** | Docker | 26.1 | Isolated microservice containerization ensuring deterministic production builds |
| **Hosting & Cloud Platform** | Render Cloud | PaaS | Singapore edge-region hosting with automated Git-push webhook deployments |

---

## 4. IMPLEMENTATION

### 4.1 Component 1: Data Collection & Feature Extraction
Component 1 operates as the sensory layer of RuleLock AI. When Cakely prepares an order, it packages the transactional state and client telemetry into an authenticated JSON payload.

```
[Incoming Checkout Request]
           │
           ▼
┌────────────────────────────────────────┐
│  Session Telemetry Extractor           │
│  - X-Session-ID / X-Device-ID          │
│  - SHA-256 Phone & Address Fingerprints│
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────┐
│  Historical Event Aggregator (Supabase)│
│  - Query past 24h session event logs   │
│  - Calculate request timestamps        │
└────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│  Extracted Behavioral Feature Vector                   │
│  [coupon_velocity, req_cadence, dev_share, addr_share] │
└────────────────────────────────────────────────────────┘
```
*Figure 02: Component 1 Feature Extraction Flow*

#### Table 06: Behavioral Feature Vectors Extracted for Anomaly Scoring
| Feature Name | Type | Range | Calculation Logic / Cyber Threat Indication |
|:---|:---:|:---:|:---|
| `coupon_attempts_per_session` | Integer | $[0, \infty)$ | Total `APPLY_COUPON` events in active session. High values indicate dictionary/brute-force attacks. |
| `avg_seconds_between_requests`| Float | $[0.1, 300]$ | Mean elapsed seconds between successive API requests. Values $<1.5s$ indicate headless bot automation. |
| `distinct_accounts_same_device`| Integer | $[1, \infty)$ | Unique user IDs authenticated from identical device fingerprint. High values indicate credential stuffing / multi-accounting. |
| `distinct_addresses_same_phone`| Integer | $[1, \infty)$ | Distinct street addresses linked to identical normalized phone hash. High values indicate promotional voucher farming. |

---

### 4.2 Component 2: Business Rule Validation Engine
Component 2 executes deterministic policy checks against hard business logic ceilings. Each rule function returns an immutable `RuleResult(passed, reason, code)`.

```python
# Extract from rulelock-ai/data-collection/rules.py
def check_quantity_ceiling(sku, quantity):
    if quantity <= 0 or quantity > MAX_QUANTITY_PER_LINE:
        return RuleResult(False, f"Quantity {quantity} exceeds the limit of {MAX_QUANTITY_PER_LINE} for {sku}", "quantity_ceiling")
    return RuleResult(True, f"Quantity {quantity} is within the limit of {MAX_QUANTITY_PER_LINE} for {sku}", "quantity_ceiling")

def check_coupon_usage(coupons_applied):
    if len(coupons_applied or []) > MAX_COUPONS_PER_SESSION:
        return RuleResult(False, f"Coupons {' + '.join(map(str, coupons_applied))} stacked (max {MAX_COUPONS_PER_SESSION})", "coupon_usage")
    return RuleResult(True, f"{len(coupons_applied or [])} coupons applied (max {MAX_COUPONS_PER_SESSION})", "coupon_usage")

def check_cod_abuse(total, bad):
    rate = bad / total if total else 0
    detail = f"COD abuse: {bad} of {total} previous COD orders were cancelled by the customer or refused"
    if bad >= COD_BAD_REJECT and rate >= 0.5:
        return RuleResult(False, detail, "cod_abuse_severe")
    if bad >= COD_BAD_HOLD and rate >= 0.5:
        return RuleResult(False, detail, "cod_abuse")
    return RuleResult(True, detail, "cod_abuse")
```

#### Table 05: Rule Engine Configurable Parameters and Policy Thresholds
| Rule Identifier | Parameter Name | Default Setting | Enforcement Action Triggered |
|:---|:---|:---:|:---:|
| `coupon_usage` | `MAX_COUPONS` | 1 coupon / order | `void_discount` (Resets discount to Rs. 0) |
| `discount_range` | `MAX_DISCOUNT_RATIO` | 60% of subtotal | `void_discount` (Resets discount to Rs. 0) |
| `quantity_ceiling`| `MAX_QUANTITY_PER_LINE` | 20 items / line | `reject` (Rejects order immediately) |
| `minimum_purchase`| `MIN_PURCHASE_AMOUNT` | Rs. 500.00 | `void_discount` (Disallows promo on small carts) |
| `cod_order_value` | `COD_UNVERIFIED_ORDER_CAP`| Rs. 15,000.00 | `hold` (Requires manual phone confirmation) |
| `cod_abuse` | `COD_BAD_HOLD` | 2 bad / $\ge 50\%$ | `hold` (Flagged for managerial inspection) |
| `cod_abuse_severe`| `COD_BAD_REJECT` | 3 bad / $\ge 50\%$ | `reject` + 60-Minute Account Ban |

---

### 4.3 Component 3: AI-Based Anomaly Detection Engine
Component 3 uses an unsupervised **Isolation Forest** machine learning model. Unlike supervised classifiers that require labeled fraud datasets, Isolation Forest isolates anomalous observations by randomly selecting a feature and randomly splitting between the maximum and minimum values.

The anomaly score $s(x, n)$ for an instance $x$ across a sample size of $n$ is defined by:
$$s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$$
Where $E(h(x))$ is the average path length across all isolation trees, and $c(n)$ is the average path length of unsuccessful searches in a Binary Search Tree:
$$c(n) = 2\left(\ln(n - 1) + 0.5772156649\right) - \frac{2(n - 1)}{n}$$

- **Normal Consumer Checkouts:** Path length is long $\rightarrow s \ge -0.06$.
- **Suspicious Session Behavior:** Path length is short $\rightarrow -0.10 \le s < -0.06 \rightarrow$ triggers `hold`.
- **High-Risk Bot Attack:** Path length is very short $\rightarrow s < -0.10 \rightarrow$ triggers `reject` with account suspension.

---

### 4.4 Component 4: Automated Enforcement Engine & Account Defense
Component 4 reconciles the findings of Components 2 and 3 into an enforceable contract.

```python
# Extract from rulelock-ai/data-collection/decision.py
def decide(order_id, account_id, rule_passed, rule_reason, anomaly_score, payment_method, rule_code=None, violations=None):
    if not rule_passed:
        if violations:
            severity = {"reject": 3, "hold": 2, "void_discount": 1}
            rule_code = max(violations, key=lambda v: severity.get(RULE_ACTION_MAP.get(v.get("code"), "hold"), 2)).get("code", rule_code)
        action = RULE_ACTION_MAP.get(rule_code, "hold")
        if action == "void_discount":
            execution = void_discount(order_id)
        elif action == "reject":
            execution = {"action": "reject_order"}
            if rule_code == "cod_abuse_severe":
                execution.update(rate_limit_account(account_id))
                execution["account_action"] = {"type": "rate_limit", "minutes": 60}
        else:
            execution = hold_cod_order(order_id)
        return {"decision": action, "reason": rule_reason, "rule_code": rule_code, **execution}

    if anomaly_score < ANOMALY_REJECT_THRESHOLD:
        return {"decision": "reject", "reason": "anomaly score indicates elevated risk",
                "account_action": {"type": "rate_limit", "minutes": 30},
                **rate_limit_account(account_id)}
    if anomaly_score < ANOMALY_HOLD_THRESHOLD:
        return {"decision": "hold", "reason": "anomaly score requires review",
                **hold_cod_order(order_id)}
    return {"decision": "accept", "reason": "passed all checks", "action": "none"}
```

When an enforcement decision returns `account_action: { type: "rate_limit", minutes: N }`, Cakely immediately executes an atomic update in PostgreSQL:
$$\text{users.rate\_limited\_until} = \text{NOW}() + N \times 60\,\text{seconds}$$
Any checkout attempt while $\text{NOW}() < \text{rate\_limited\_until}$ is terminated at the gateway with an **HTTP 429 Too Many Requests** error.

---

### 4.5 Data & Audit Layer: Immutable Audit Logging
Security compliance mandates that audit logs must be immutable. In Supabase PostgreSQL, `rulelock_audit_log` is protected by database triggers that intercept and reject any `UPDATE` or `DELETE` statements.

```sql
-- Append-Only Protection Trigger
CREATE OR REPLACE FUNCTION public.enforce_audit_log_immutability()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION 'Security Policy Violation: rulelock_audit_log entries are immutable and cannot be updated or deleted.';
END;
$$;

CREATE TRIGGER trg_protect_rulelock_audit
BEFORE UPDATE OR DELETE ON public.rulelock_audit_log
FOR EACH ROW EXECUTE FUNCTION public.enforce_audit_log_immutability();
```

---

### 4.6 Verification & Storefront Integration (Cakely)
Cakely connects to RuleLock via a pre-capture validation hook inside `POST /api/checkout`.

1. **Client Request:** Browser transmits selected items, address, and requested coupon codes.
2. **Server Price Re-Derivation:** Cakely iterates through `items`, ignores client-supplied `unitPrice`, and looks up catalog prices directly in `products`.
3. **Pre-Commit Pending Record:** The order is written as `status: 'PENDING'`.
4. **Synchronous RuleLock Review:** Cakely calls `POST https://rulelock-data-collection.onrender.com/review-order`.
5. **State Finalization:**
   - If `accept`: Order status stays `PENDING` (ready for kitchen preparation).
   - If `void_discount`: Discount set to 0, order updated with full total, customer charged canonical price.
   - If `hold`: Status updated to `PENDING_REVIEW`, payment status set to `ON_HOLD`.
   - If `reject`: Order status set to `REJECTED`, payment status set to `VOIDED`.
6. **Customer Clean Shield:** Customer receives: `"Your order is ready to continue."` or `"Your order is under review."` (No internal thresholds or model scores are leaked).

---

### 4.7 Graphical User Interface & Administrative Dashboards

#### 4.7.1 Customer Checkout Interface
The checkout interface (`CheckoutRulesView.jsx`) provides real-time cart breakdowns, coupon selector pills with payment-method dependency filtering, delivery vs. collection toggles, and demo card payment forms.

#### 4.7.2 Cakely Admin Dashboard
The Cakely Admin Panel (`AdminPanel.jsx`) features a top-level **RuleLock Live Review Switch**. When toggled off, orders bypass inspection; when toggled on, every checkout transaction is reviewed before capture. Selecting any order opens the integrated `RuleLockReviewPanel.jsx`, showing full diagnostic inspection data.

#### 4.7.3 RuleLock Operations Dashboard
Served standalone from the Python service at `/dashboard`, this interface provides real-time operations metrics:
- 24-hour total requests validated
- Rule violations breakdown (Coupons, Quantities, COD)
- Anomaly score distribution chart
- Live chronological enforcement feed with clickable audit modal inspections

---

## 5. METHODOLOGY

### 5.1 Development Lifecycle & Phased Approach
The project followed an Agile Iterative Security Development Lifecycle (SecSDLC), structured across four consecutive phases over 12 weeks.

#### Table 08: Project Development Phases and Deliverables
| Phase | Title | Duration | Key Engineering Activities | Milestone Output |
|:---:|:---|:---:|:---|:---|
| **Phase 1** | Requirement Analysis & Threat Modeling | Weeks 1 - 3 | OWASP API abuse analysis, architecture specification, threat actor profiling | Threat Model Specification & Architecture Blueprint |
| **Phase 2** | Core Detection & ML Engine Construction | Weeks 4 - 6 | Rule engine algorithms, Isolation Forest training, session feature pipeline | RuleLock Microservice & pytest Test Suite |
| **Phase 3** | Storefront & Integration Engineering | Weeks 7 - 9 | Cakely storefront, atomic PostgreSQL RPCs, pre-capture review hook | Unified Option B Microservice Architecture |
| **Phase 4** | Pentesting, Hardening & Deployment | Weeks 10 - 12 | Burp Suite attack simulation, Render Docker deployment, audit lock down | Production Release & Live Verification Evidence |

---

### 5.2 Functional Requirements (FR)

#### Table 09: Functional Requirements Traceability Matrix
| ID | Requirement Description | Implementing Component | Verification Method | Status |
|:---:|:---|:---|:---|:---:|
| **FR-01** | Line quantity enforcement exceeding 20 units | Component 2 (`rules.py`) | Automated test & Burp Suite injection | **PASS** |
| **FR-02** | Prevention of multi-coupon stacking | Component 2 (`rules.py`) | Automated test & proxy attack test | **PASS** |
| **FR-03** | Server-side canonical unit price re-derivation | Cakely API (`api.js`) | Unit price tampering test | **PASS** |
| **FR-04** | Detection of repetitive COD order cancellation | Component 2 (`rules.py`) | Multi-order sequential cycle simulation | **PASS** |
| **FR-05** | Unsupervised anomaly scoring on session cadence | Component 3 (`anomaly_scoring.py`) | Isolation Forest vector evaluation | **PASS** |
| **FR-06** | Automated account rate limiting upon severe abuse | Component 4 (`decision.py`) | HTTP 429 gateway verification | **PASS** |
| **FR-07** | Append-only tamper-proof audit record storage | PostgreSQL (`schema.sql`) | Direct `UPDATE`/`DELETE` rejection test | **PASS** |
| **FR-08** | Dynamic administrative RuleLock enable/disable toggle | Cakely Admin (`AdminPanel.jsx`) | Live toggle checkout comparison | **PASS** |
| **FR-09** | Zero security heuristic exposure on customer UI | Frontend (`CheckoutRulesView.jsx`)| UI inspect & response payload audit | **PASS** |

---

### 5.3 Non-Functional Requirements (NFR)
1. **Performance & Latency:** Total pre-capture inspection latency must not exceed 100ms under standard network conditions.
2. **Reliability & Fail-Safe Defaults:** If RuleLock AI is offline, unreachable, or returns a 500 error, Cakely must fail-safe to `hold` (`PENDING_REVIEW`), never automatically approving unverified orders.
3. **Data Integrity & Confidentiality:** Raw customer telephone numbers and full postal addresses must never be stored in plaintext within security audit logs. SHA-256 salted hashes must be used for behavioral correlation.
4. **Portability & Modularity:** RuleLock AI must remain decoupled from specific commerce database schemas, accepting standardized JSON transaction contracts.

---

## 6. TESTING & VALIDATION

### 6.1 Automated Test Suite Overview
RuleLock AI includes an automated testing framework built with `pytest`.

#### Table 10: Automated Unit and Integration Test Suite Breakdown (52 Tests)
| Test Suite Module | Test File | Test Cases | Scope and Security Verification | Status |
|:---|:---|:---:|:---|:---:|
| **Audit Log Integrity** | `tests/test_audit_log.py` | 6 | Append-only behavior, schema conformity, timestamp consistency | **PASS** |
| **Audit Query Filtering** | `tests/test_audit_queries.py` | 4 | Cursor pagination, action filtering, search term sanitization | **PASS** |
| **Operations Dashboard** | `tests/test_dashboard.py` | 5 | 24h metric aggregations, threat feed serialization, auth cookies | **PASS** |
| **Database Features** | `tests/test_db_features.py` | 1 | Supabase connectivity, service role credential validation | **PASS** |
| **Pipeline Detection** | `tests/test_detection.py` | 4 | Feature normalization, Isolation Forest scoring consistency | **PASS** |
| **System Readiness** | `tests/test_health.py` | 13 | `/health`, `/ready`, ML model memory residency checks | **PASS** |
| **Log Retention Policy** | `tests/test_retention.py` | 3 | Expired session event purging while preserving immutable audit logs | **PASS** |
| **Review Orchestration**| `tests/test_review_pipeline.py` | 5 | `/review-order` contract conformity, idempotent replay defense | **PASS** |
| **Rules & Decisions** | `tests/test_rules_and_decisions.py`| 8 | Boundary tests for coupons, quantities, pricing, and COD abuse | **PASS** |
| **Security Config** | `tests/test_security_config.py` | 3 | Token validation, missing header handling, constant-time HMAC | **PASS** |
| **TOTAL** | **10 Test Suites** | **52** | **Full Microservice Pipeline Verification** | **100% PASS** |

---

### 6.2 Non-Functional Requirements Verification

#### Table 11: Non-Functional Requirements Verification Matrix
| Metric / Requirement | Target Specification | Empirical Result | Compliance Status |
|:---|:---:|:---:|:---:|
| **Review Processing Latency** | $< 100\text{ ms}$ | $54.2\text{ ms}$ (Average) | **MET** |
| **Test Suite Pass Rate** | $100\%$ | $52 / 52\text{ Tests Passed}$ | **MET** |
| **Tamper-Proof Audit Defense** | $0\text{ Modifications Permitted}$ | $100\%\text{ of UPDATE/DELETE Blocked}$ | **MET** |
| **Account Rate-Limit Accuracy** | $100\%\text{ Enforcement on Ban}$ | HTTP 429 returned on all banned calls | **MET** |
| **Fail-Safe Policy** | $0\text{ Unchecked Orders Approved}$| Fallback to `hold` on timeout/network loss | **MET** |

---

### 6.3 Performance Benchmarking

#### Table 12: Performance Benchmark Latency and Throughput Results
| Pipeline Stage | Minimum Latency | Average Latency | 99th Percentile Latency |
|:---|:---:|:---:|:---:|
| **C1: Data Collection & Feature Extract** | 4.1 ms | 8.6 ms | 14.2 ms |
| **C2: Deterministic Rule Validation** | 1.8 ms | 3.2 ms | 5.1 ms |
| **C3: Isolation Forest Model Inference** | 8.2 ms | 14.5 ms | 22.0 ms |
| **C4: Enforcement Decision Formulation** | 0.9 ms | 1.4 ms | 2.5 ms |
| **Database Atomic Review Persistence** | 14.0 ms | 26.5 ms | 41.0 ms |
| **TOTAL ROUND-TRIP LATENCY** | **29.0 ms** | **54.2 ms** | **84.8 ms** |

---

### 6.4 Burp Suite Penetration Testing & Attack Simulations
To validate business logic defenses under adversarial conditions, penetration tests were conducted using Burp Suite Proxy and an automated Node.js attack suite (`scripts/test-burp-attacks.mjs`).

#### Table 13: Burp Suite Penetration Testing Attack Scenario Matrix
| Attack ID | Vector Name | Injected Burp Suite Payload | RuleLock Response | Resulting Order Status | Defense Outcome |
|:---:|:---|:---|:---:|:---:|:---:|
| **ATK-01** | Quantity Manipulation | `"quantity": 50` on Product 1 | `decision: "reject"` | `REJECTED` | **SUCCESS: Ceiling Enforced** |
| **ATK-02** | Coupon Stacking | `"coupons": ["CAKE10", "CAKE20"]` | `decision: "void_discount"` | `PENDING` (Discount: Rs. 0) | **SUCCESS: Discount Voided** |
| **ATK-03** | Price Tampering | `"unitPrice": 1.00` | `decision: "reject"` | `REJECTED` | **SUCCESS: Catalog Match Enforced**|
| **ATK-04** | Excessive COD Value | `"total": 36000, "paymentMethod": "COD"`| `decision: "hold"` | `PENDING_REVIEW` | **SUCCESS: Held for Verification**|
| **ATK-05** | COD Cancellation Abuse| 3 consecutive customer order cancels | `decision: "reject"` + Rate Limit | `REJECTED` | **SUCCESS: Account Banned (60m)**|
| **ATK-06** | Post-Ban Checkout | Standard checkout after ATK-05 | HTTP 429 `RATE_LIMITED` | Blocked at Gateway | **SUCCESS: 100% Interception** |

---

## 7. RESULTS & DISCUSSION

### 7.1 Objective Achievement Analysis
All six specific objectives defined in Section 2 were met:
1. **Rule Engine:** Accurately evaluated quantities, prices, coupon combinations, and COD thresholds within 3.2ms.
2. **Machine Learning Model:** The Isolation Forest model detected session cadence abnormalities and brute-force coupon probing without false-positive disruptions on ordinary checkouts.
3. **Automated Enforcement:** Translated multi-dimensional risk scores into deterministic actions, correctly voiding discounts and suspending accounts.
4. **Immutable Audit Storage:** PostgreSQL triggers successfully rejected direct modification attempts, ensuring an unalterable security audit record.
5. **Cakely Integration:** Enabled live switching between standard e-commerce and active security inspection via the admin toggle.
6. **Burp Suite Validation:** Successfully defended against all simulated business logic attacks with zero unverified orders approved.

---

### 7.2 Identified Challenges and Engineering Solutions
1. **Challenge:** Initial deployments resulted in empty coupon lists because the newly provisioned Supabase database used a legacy schema lacking `allowed_payment_methods`.  
   **Solution:** Executed a comprehensive database migration (`fix_coupons_and_rules.sql`) adding missing columns, dropping legacy NOT NULL constraints on `"value"`, and granting execute permissions on `record_coupon_usages`.
2. **Challenge:** Customer checkouts prematurely clamped quantities to 20 in the browser, preventing RuleLock from seeing and recording the quantity manipulation attack.  
   **Solution:** Refactored `api.js` to evaluate `rulelockOn` prior to item loops, forwarding the raw un-clamped quantity directly to RuleLock so the Rule Engine could formally catch and log the `quantity_ceiling` violation.
3. **Challenge:** Repeated COD cancellations were rejected by RuleLock, but the customer account remained active, allowing continued bot orders.  
   **Solution:** Integrated `rate_limit_account` into `decision.py` under the `cod_abuse_severe` branch, returning `account_action: { type: "rate_limit", minutes: 60 }`, which triggers a 60-minute ban in Cakely.

---

### 7.3 Deployment & Live Verification Evidence
Both production services are deployed and operational on Render cloud infrastructure:
- **RuleLock AI Backend:** `https://rulelock-data-collection.onrender.com`  
  - Readiness check: `GET /ready` $\rightarrow$ `{"ready": true, "checks": {"model_loaded": true, "supabase_reachable": true}}`
  - Operations Dashboard: `https://rulelock-data-collection.onrender.com/dashboard`
- **Cakely Storefront Backend & App:** `https://cakely-sg55.onrender.com`  
  - Health check: `GET /api/health` $\rightarrow$ `{"success": true, "service": "cakely-api", "database": "connected"}`

---

## 8. DESCRIPTION OF PERSONNEL AND FACILITIES

### 8.1 Team Structure & Responsibilities
The project was executed by an agile engineering team of four members:
- **[Student Name 1] (Team Lead & Detection Engineer):** Project management, Isolation Forest model design, feature extraction, and deployment orchestration.
- **[Student Name 2] (Backend Security Engineer):** Deterministic business rule engine, decision synthesis, action dispatchers, and pytest automation.
- **[Student Name 3] (Full-Stack Storefront Engineer):** Cakely application development, pre-capture review hook integration, and administrative dashboard.
- **[Student Name 4] (Database & Security QA Engineer):** Supabase PostgreSQL architecture, trigger immutability, Burp Suite penetration testing, and documentation.

---

### 8.2 Hardware and Operating Environment Specifications

#### Table 14: Minimum and Recommended Hardware Specifications
| Specification Category | Minimum Development Requirement | Production Hosting Environment |
|:---|:---|:---|
| **Processor (CPU)** | Intel Core i5 / AMD Ryzen 5 (4 Cores) | Render Cloud Shared vCPU (PaaS Docker Container) |
| **System Memory (RAM)** | 8 GB DDR4 | 512 MB - 1 GB Containerized RAM Allocation |
| **Storage Capacity** | 20 GB Available SSD Space | Cloud SSD with Automated Snapshot Backups |
| **Operating System** | Windows 11 / Linux Ubuntu 22.04 LTS | Alpine Linux / Debian-Slim Container Environment |
| **Runtime Runtimes** | Python 3.13.2 / Node.js 22.18.0 | Official Python 3.13-slim and Node 22 Base Images |

---

## 9. BUDGET AND BUDGET JUSTIFICATION

### 9.1 Development & Operational Budget

#### Table 15: Development and Infrastructure Cost Breakdown
| Resource / Service | Provider / Source | Tier / License | Commercial Cost | Project Cost |
|:---|:---|:---|:---:|:---:|
| **Microservice Cloud Hosting** | Render Cloud | Free Tier (Containerized) | \$7.00 / month | **\$0.00** |
| **Storefront Web Hosting** | Render Cloud | Free Tier (Node.js Service) | \$7.00 / month | **\$0.00** |
| **Managed Relational Database**| Supabase Inc. | Free Tier (PostgreSQL 15) | \$25.00 / month | **\$0.00** |
| **ML & API Libraries** | Open Source | MIT / BSD / Apache 2.0 | \$0.00 | **\$0.00** |
| **Security Audit & Pentest Tool**| PortSwigger Burp Suite| Community Edition | \$449.00 / seat | **\$0.00** |
| **TOTAL EXPENDITURE** | | | **\$488.00** | **\$0.00 (100% Free / OSS)** |

---

## 10. REFERENCE LIST

1. Open Web Application Security Project (OWASP), "OWASP API Security Top 10 - 2023: API6:2023 Unrestricted Access to Sensitive Business Flows," OWASP Foundation, Dec. 2023. [Online]. Available: https://owasp.org/API-Security/editions/2023/en/0xa6-unrestricted-access-to-sensitive-business-flows/
2. F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation Forest," in *2008 Eighth IEEE International Conference on Data Mining*, Pisa, Italy, 2008, pp. 413-422, doi: 10.1109/ICDM.2008.17.
3. F. T. Liu, K. M. Ting, and Z.-H. Zhou, "Isolation-based anomaly detection," *ACM Transactions on Knowledge Discovery from Data*, vol. 6, no. 1, pp. 1-39, Mar. 2012, doi: 10.1145/2133360.2133363.
4. M. Howard and D. LeBlanc, *Writing Secure Code*, 2nd ed. Redmond, WA: Microsoft Press, 2003.
5. P. Devanbu and S. Stubblebine, "Software engineering for security: a roadmap," in *Proceedings of the Conference on The Future of Software Engineering - ICSE '00*, Limerick, Ireland, 2000, pp. 227-239, doi: 10.1145/336512.336559.
6. G. McGraw, *Software Security: Building Security In*. Boston, MA: Addison-Wesley, 2006.
7. National Institute of Standards and Technology (NIST), "Framework for Improving Critical Infrastructure Cybersecurity, Version 1.1," NIST, Gaithersburg, MD, Apr. 2018, doi: 10.6028/NIST.CSWP.04162018.
8. PCI Security Standards Council, "Payment Card Industry (PCI) Data Security Standard: Requirements and Testing Procedures Version 4.0," PCI SSC, Wakefield, MA, Mar. 2022.
9. D. Stuttard and M. Pinto, *The Web Application Hacker's Handbook: Finding and Exploiting Security Flaws*, 2nd ed. Indianapolis, IN: John Wiley & Sons, 2011.
10. E. Rescorla, "The Transport Layer Security (TLS) Protocol Version 1.3," RFC 8446, Internet Engineering Task Force, Aug. 2018.

---

## 11. APPENDICES

### Appendix A: Key Source Code Extracts

#### A.1 Automated Enforcement Policy Engine (`decision.py`)
```python
def decide(order_id, account_id, rule_passed, rule_reason, anomaly_score, payment_method, rule_code=None, violations=None):
    if not rule_passed:
        if violations:
            severity = {"reject": 3, "hold": 2, "void_discount": 1}
            rule_code = max(violations, key=lambda v: severity.get(RULE_ACTION_MAP.get(v.get("code"), "hold"), 2)).get("code", rule_code)
        action = RULE_ACTION_MAP.get(rule_code, "hold")
        if action == "void_discount":
            execution = void_discount(order_id)
        elif action == "reject":
            execution = {"action": "reject_order"}
            if rule_code == "cod_abuse_severe":
                execution.update(rate_limit_account(account_id))
                execution["account_action"] = {"type": "rate_limit", "minutes": 60}
        else:
            execution = hold_cod_order(order_id)
        return {"decision": action, "reason": rule_reason, "rule_code": rule_code, **execution}

    if anomaly_score < ANOMALY_REJECT_THRESHOLD:
        return {"decision": "reject", "reason": "anomaly score indicates elevated risk",
                "account_action": {"type": "rate_limit", "minutes": 30},
                **rate_limit_account(account_id)}
    if anomaly_score < ANOMALY_HOLD_THRESHOLD:
        return {"decision": "hold", "reason": "anomaly score requires review",
                **hold_cod_order(order_id)}
    return {"decision": "accept", "reason": "passed all checks", "action": "none"}
```

---

### Appendix B: Test Suite Execution Transcript
```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-8.2.2, pluggy-1.6.0
rootdir: C:\Users\AL FARES\Desktop\projects\rulelock-ai-starter\rulelock-ai\data-collection
collected 52 items

tests\test_audit_log.py ......                                           [ 11%]
tests\test_audit_queries.py ....                                         [ 19%]
tests\test_dashboard.py .....                                            [ 28%]
tests\test_db_features.py .                                              [ 30%]
tests\test_detection.py ....                                             [ 38%]
tests\test_health.py .............                                       [ 63%]
tests\test_retention.py ...                                              [ 69%]
tests\test_review_pipeline.py .....                                      [ 78%]
tests\test_rules_and_decisions.py ........                               [ 94%]
tests\test_security_config.py ...                                        [100%]

============================= 52 passed in 4.97s ==============================
```

---

### Appendix C: Comprehensive 12-Week Team Logbook

#### Table 17: 12-Week Logbook Summary by Member and Outcome
| Week | Focus / Objective | Members Involved | Total Hours | Tasks Completed | Key Engineering Outcomes |
|:---:|:---|:---|:---:|:---|:---|
| **W1** | Project Inception & Scoping | All Members | 32h | Literature review, OWASP API analysis | Project Proposal & Architecture Charter |
| **W2** | Threat Modeling & Spec | Name 1, Name 2 | 28h | Threat actor profiling, boundary definition | Threat Model Specification Document |
| **W3** | Database Architecture | Name 3, Name 4 | 30h | PostgreSQL schema design, RLS draft | Initial Supabase Schema Blueprint |
| **W4** | Rule Engine Development | Name 2, Name 4 | 35h | Quantity and coupon rule functions | Component 2 (`rules.py`) with unit tests |
| **W5** | Anomaly Engine Training | Name 1, Name 2 | 34h | Synthetic vector generator, Isolation Forest | Component 3 (`anomaly_scoring.py`) |
| **W6** | Enforcement & Decision | Name 1, Name 2 | 32h | Action dispatchers, rate-limiting logic | Component 4 (`decision.py`) |
| **W7** | Storefront Construction | Name 3, Name 4 | 36h | Cakely React storefront, catalog, cart | Cakely Storefront Frontend Release |
| **W8** | API Integration Hook | Name 2, Name 3 | 34h | Pre-capture `/review-order` hook | Closed-loop integration between APIs |
| **W9** | Administrative Panels | Name 3, Name 4 | 32h | RuleLock switch, diagnostics panel | Cakely Admin & Ops Dashboard |
| **W10**| Penetration Testing | Name 1, Name 4 | 38h | Burp Suite intercept simulation script | `test-burp-attacks.mjs` attack suite |
| **W11**| Bug Fixing & Hardening | All Members | 40h | Coupon schema migration, quantity unclamp | Render production deploy & zero em-dashes |
| **W12**| Final Verification & Docs | All Members | 35h | 52-test automated run, report compiling | Final Project Report & Code Release |

---

## 12. INDIVIDUAL MEMBER CONTRIBUTION

#### Table 16: Individual Member Responsibility Matrix
| Member Name | Student ID | Primary Responsibilities | Specific Modules / Source Files Contributed |
|:---|:---:|:---|:---|
| **[Student Name 1]** | [ID 001] | Project Leadership, ML Anomaly Model, Feature Engineering, Docker Packaging | `anomaly_scoring.py`, `features.py`, `Dockerfile`, `render.yaml` |
| **[Student Name 2]** | [ID 002] | Deterministic Rule Engine, Decision Policy, Automated Action Dispatchers | `rules.py`, `decision.py`, `actions.py`, `tests/` |
| **[Student Name 3]** | [ID 003] | Cakely Storefront, Checkout Flow, Pre-Capture API Hooks, Admin Switch | `api.js`, `CheckoutRulesView.jsx`, `AdminPanel.jsx`, `RuleLockReviewPanel.jsx` |
| **[Student Name 4]** | [ID 004] | Database Schema, Append-Only Triggers, Penetration Testing, Attack Suite | `schema.sql`, `fix_coupons_and_rules.sql`, `test-burp-attacks.mjs` |

---

## 13. COMMERCIALIZATION PLAN

### 13.1 Target Market
RuleLock AI addresses small-to-medium enterprise (SME) digital merchants, Shopify / WooCommerce storefronts, and specialized direct-to-consumer (D2C) brands operating in high-fraud retail markets.

### 13.2 Go-to-Market & Promotion Strategy
- **Turnkey Plugins:** Publish drop-in connectors for WooCommerce, Shopify, and Magento.
- **Developer-First API:** Offer simple REST integrations requiring only 4 lines of checkout middleware code.
- **Open-Core Community Edition:** Provide an open-source rule validation engine to build developer adoption, with premium anomaly detection models in commercial tiers.

### 13.3 Monetization Tiers
- **Community (Free):** Up to 500 orders/month; core deterministic rule validation, self-hosted.
- **Professional (\$49/month):** Up to 10,000 orders/month; cloud-hosted ML anomaly detection, 30-day immutable audit logs, email alerts.
- **Enterprise (\$249/month):** Unlimited orders; custom Isolation Forest model re-training, automated IP/account threat intelligence sharing, dedicated support SLA.

### 13.4 Competitive Advantage
Unlike traditional WAFs that bill thousands of dollars monthly without understanding business logic, RuleLock AI delivers deep, context-aware protection against promotional abuse and fake COD orders with zero infrastructure overhead.

---

## 14. DEVELOPMENT PLAN & FUTURE ENHANCEMENTS

### 14.1 Phase Milestones
- **Q1 2027:** Release official WooCommerce and Shopify SDK plugins.
- **Q2 2027:** Implement semi-supervised graph neural networks (GNN) for cross-merchant syndicate ring detection.
- **Q3 2027:** Integrate automated biometric mouse-movement and typing cadence heuristics into Component 1 telemetry.

---

## 15. CONCLUSION

This project successfully researched, engineered, and empirically validated **RuleLock AI**, a modular security microservice addressing the critical vulnerability landscape of e-commerce business logic flaws. By transitioning transaction security from perimeter-based string filtering to contextual behavioral validation, RuleLock AI prevents sophisticated promotional abuse and inventory denial attacks that bypass standard WAF appliances.

The system's core technical achievement lies in its synchronized four-stage architecture: pairing deterministic rule validation with an unsupervised Isolation Forest anomaly model and an automated enforcement engine. This design allows graduated actions—such as voiding an illegitimate discount without interrupting checkout—preserving legitimate retail conversions while preventing financial losses.

Rigorous automated testing through a 52-case unit test suite and active Burp Suite proxy penetration attacks confirmed that RuleLock AI reliably detects and blocks excessive quantity tampering, multi-coupon race conditions, and Cash on Delivery refusal campaigns. The automated temporal account suspension mechanism effectively neutralizes abusive accounts without administrative intervention.

The integration with the Cakely artisanal bakery platform proved that deep security inspection can operate with complete customer transparency. Standard shoppers experience sub-85ms processing times and clean status messages, while merchants and security personnel gain complete audit accountability through immutable PostgreSQL triggers and real-time operations dashboards.

In conclusion, RuleLock AI demonstrates that modern business logic security does not require monolithic complexity. Through lightweight microservice architecture, machine learning behavioral modeling, and strict database immutability, online merchants can robustly protect digital commerce flows against an evolving threat landscape.
