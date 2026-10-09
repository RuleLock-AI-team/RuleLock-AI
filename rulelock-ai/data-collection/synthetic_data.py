"""
Synthetic training data.

Stated limitation per the proposal: the normal-behaviour baseline should
come from a real public e-commerce/transactions dataset once sourced (see
anomaly-detection/README.md); synthetic abuse sequences represent the
abnormal class in the meantime so training and evaluation can start
immediately.

Merged in from the standalone anomaly-detection service.
"""
import numpy as np


def generate_normal_sessions(n=500, seed=42):
    rng = np.random.default_rng(seed)
    return np.column_stack([
        rng.poisson(0.8, n).clip(0, 5),
        # Long pauses are routine: use a broad, right-skewed normal range.
        rng.lognormal(np.log(35), 1.0, n).clip(1, 600),
        rng.choice([1, 2], n, p=[0.97, 0.03]),
        rng.choice([1, 2], n, p=[0.97, 0.03]),
    ])


def generate_abuse_sessions(n=50, seed=7):
    rng = np.random.default_rng(seed)
    return np.column_stack([
        rng.poisson(6, n),                 # many coupon attempts
        rng.normal(3, 1, n).clip(0.1),
        rng.integers(3, 8, n),             # several accounts, one device
        rng.integers(3, 8, n),             # several addresses, one phone
    ])
