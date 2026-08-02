# Component 3 — AI-Based Anomaly Detection
**Owner: Nihara**

Catches what the rule engine can't by design: abuse spread across
multiple accounts/sessions to stay under any single-account threshold.

## Run locally
```bash
pip install -r requirements.txt
python train_model.py    # produces model.joblib
python score_service.py  # http://localhost:5003
pytest
```

## What's implemented
- Working synthetic normal/abuse data generators
- A trained, tested Isolation Forest (`train_model.py`) — the test proves
  it scores abuse-shaped sessions as more anomalous than normal ones
- A scoring API wrapping the model

## What to build here (the real coursework)
- Source a real public e-commerce/transactions dataset (e.g. Kaggle) as
  the normal-behaviour baseline, replacing `generate_normal_sessions()`
- `session_to_features()` — pull real values from Charuka's data pipeline
  instead of expecting pre-computed inputs
- Evaluate with precision/recall/false-positive-rate; tune the anomaly
  threshold used downstream by the enforcement engine
- Optionally compare against a One-Class SVM per the proposal
