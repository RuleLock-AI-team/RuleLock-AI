# Component 2 — Business Rule Validation Engine
**Owner: Sadini**

Explicit rule checks: coupon usage, discount range, quantity ceiling,
minimum purchase, plus the two COD-specific rules.

## Run locally
```bash
pip install -r requirements.txt
python app.py        # http://localhost:5002
pytest                # run the rule tests
```

## What's implemented
- `check_quantity_ceiling()` and `check_minimum_purchase()` — working, tested

## What to build here (the real coursework)
- `check_coupon_usage()`, `check_discount_range()`
- The two COD-specific rules: `check_cod_order_value()`, `check_cod_refusal_rate()`
- `validate_transaction()` — aggregate all six into one result
- Write pytest cases for every rule, normal and abusive inputs, per the proposal
