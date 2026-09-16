from thai_spoof.metrics import calculate_metrics


def test_perfect_scores_have_zero_eer() -> None:
    metrics = calculate_metrics(
        ["spoof", "spoof", "bonafide", "bonafide"],
        [-2.0, -1.0, 1.0, 2.0],
    )
    assert metrics["eer"] == 0.0
    assert metrics["roc_auc"] == 1.0

