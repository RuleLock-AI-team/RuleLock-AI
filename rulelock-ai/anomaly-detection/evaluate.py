"""
RuleLock AI - Component 3: model evaluation & threshold calibration 
Owner: Nihara
"""
import numpy as np
import joblib
from sklearn.metrics import precision_recall_curve
from synthetic_data import generate_normal_sessions, generate_abuse_sessions

def evaluate():
    model = joblib.load("model.joblib")

    normal = generate_normal_sessions(n=200, seed=101)   # held-out, different seed
    abuse = generate_abuse_sessions(n=50, seed=202)

    normal_scores = model.decision_function(normal)
    abuse_scores = model.decision_function(abuse)

    print(f"Normal sessions — mean score: {normal_scores.mean():.3f}, "
          f"min: {normal_scores.min():.3f}, max: {normal_scores.max():.3f}")
    print(f"Abuse sessions  — mean score: {abuse_scores.mean():.3f}, "
          f"min: {abuse_scores.min():.3f}, max: {abuse_scores.max():.3f}")

    y_true = np.concatenate([np.zeros(len(normal)), np.ones(len(abuse))])
    all_scores = np.concatenate([normal_scores, abuse_scores])
    # lower raw_score = more anomalous, so flip sign for "higher = more abusive"
    y_scores = -all_scores

    precision, recall, thresholds = precision_recall_curve(y_true, y_scores)

    # pick threshold balancing precision/recall (tune this by hand later)
    f1 = 2 * precision * recall / (precision + recall + 1e-9)
    best_idx = np.argmax(f1)
    best_threshold = thresholds[best_idx] if best_idx < len(thresholds) else thresholds[-1]

    print(f"\nSuggested raw_score threshold (flag as abuse if raw_score < "
          f"{-best_threshold:.3f}): precision={precision[best_idx]:.2f}, "
          f"recall={recall[best_idx]:.2f}")


if __name__ == "__main__":
    evaluate()
