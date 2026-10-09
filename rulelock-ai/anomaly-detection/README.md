# LEGACY: anomaly detection service

This folder is a retained legacy copy and is not deployed. The deployed anomaly feature extraction, model training, and scoring code lives in `data-collection/` (`features.py`, `train_model.py`, and `anomaly_scoring.py`). Do not make production changes here.

## Model limitations

The deployed model is trained on synthetic sessions. Its evaluation compares models and fixture labels authored from the same assumptions, so the results are circular and are not evidence of real-world detection quality. See `data-collection/evaluate.py` and `docs/architecture.md`.
