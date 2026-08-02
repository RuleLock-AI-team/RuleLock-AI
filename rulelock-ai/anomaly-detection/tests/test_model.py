import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from train_model import train


def test_model_scores_abuse_pattern_as_more_anomalous_than_normal():
    model = train()
    normal_score = model.decision_function([[1, 30, 1, 1]])[0]
    abuse_score = model.decision_function([[8, 2, 5, 5]])[0]
    # IsolationForest: lower decision_function score = more anomalous
    assert abuse_score < normal_score
