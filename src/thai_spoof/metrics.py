from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve


LABEL_TO_INT = {"spoof": 0, "bonafide": 1}


def calculate_metrics(labels: list[str], bonafide_scores: list[float]) -> dict[str, object]:
    if len(labels) != len(bonafide_scores):
        raise ValueError("labels and scores must have equal lengths")
    if not labels:
        raise ValueError("at least one labeled score is required")

    unknown = sorted(set(labels) - LABEL_TO_INT.keys())
    if unknown:
        raise ValueError(f"unsupported labels: {unknown}")

    y_true = np.asarray([LABEL_TO_INT[label] for label in labels], dtype=np.int64)
    scores = np.asarray(bonafide_scores, dtype=np.float64)
    if np.unique(y_true).size != 2:
        raise ValueError("metrics require both bonafide and spoof examples")

    false_positive_rate, true_positive_rate, thresholds = roc_curve(y_true, scores)
    false_negative_rate = 1.0 - true_positive_rate
    index = int(np.nanargmin(np.abs(false_positive_rate - false_negative_rate)))
    eer = float((false_positive_rate[index] + false_negative_rate[index]) / 2.0)
    threshold = float(thresholds[index])
    predictions = (scores >= threshold).astype(np.int64)

    return {
        "count": int(y_true.size),
        "eer": eer,
        "eer_percent": eer * 100.0,
        "eer_threshold": threshold,
        "roc_auc": float(roc_auc_score(y_true, scores)),
        "accuracy_at_eer_threshold": float(accuracy_score(y_true, predictions)),
        "confusion_matrix_spoof_bonafide": confusion_matrix(
            y_true, predictions, labels=[0, 1]
        ).tolist(),
    }

