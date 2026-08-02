"""
Synthetic training data.

Stated limitation per the proposal: the normal-behaviour baseline
should come from a real public e-commerce/transactions dataset once
sourced (see README); synthetic abuse sequences represent the abnormal
class in the meantime so training and evaluation can start immediately.
"""
import numpy as np


def generate_normal_sessions(n=500, seed=42):
    rng = np.random.default_rng(seed)
    return np.column_stack([
        rng.poisson(1, n),                 # coupon_attempts_per_session
        rng.normal(30, 10, n).clip(1),     # avg_seconds_between_requests
        rng.integers(1, 2, n),             # distinct_accounts_same_device
        rng.integers(1, 2, n),             # distinct_addresses_same_phone
    ])


def generate_abuse_sessions(n=50, seed=7):
    rng = np.random.default_rng(seed)
    return np.column_stack([
        rng.poisson(6, n),                 # many coupon attempts
        rng.normal(3, 1, n).clip(0.1),     # rapid-fire requests
        rng.integers(3, 8, n),             # several accounts, one device
        rng.integers(3, 8, n),             # several addresses, one phone
    ])
