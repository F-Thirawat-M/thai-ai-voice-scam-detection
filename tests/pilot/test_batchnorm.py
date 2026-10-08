import pytest
import torch
from torch import nn

from thai_spoof.pilot.batchnorm import configure_training_mode, snapshot_bn_buffers, summarize_bn_changes


@pytest.mark.parametrize("mode", ["train", "frozen"])
def test_only_batchnorm_mode_changes_and_affine_parameters_still_learn(mode):
    torch.manual_seed(42)
    model = nn.Sequential(nn.BatchNorm1d(3), nn.Dropout(0.2), nn.Linear(3, 2))
    before = snapshot_bn_buffers(model)
    original = model[0].weight.detach().clone()
    model.eval()
    assert configure_training_mode(model, mode) == 1
    assert model.training and model[1].training and model[2].training
    assert model[0].training == (mode == "train")
    assert model[0].weight.requires_grad and model[0].bias.requires_grad
    x = torch.randn(12, 3) + 2
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    model(x).square().mean().backward()
    assert torch.isfinite(model[0].weight.grad).all()
    optimizer.step()
    assert not torch.equal(model[0].weight.detach(), original)
    summary = summarize_bn_changes(before, snapshot_bn_buffers(model))
    assert bool(summary["changed_buffer_count"]) == (mode == "train")
    assert summary["num_batches_tracked_deltas"]["0.num_batches_tracked"] == int(mode == "train")


def test_invalid_mode_does_not_mutate_model():
    model = nn.Sequential(nn.BatchNorm1d(2), nn.Dropout())
    model.eval()
    with pytest.raises(ValueError, match="mode"):
        configure_training_mode(model, "all_eval")
    assert not model.training and not model[1].training


@pytest.mark.parametrize("model", [nn.Linear(2, 2), nn.BatchNorm1d(2, track_running_stats=False)])
def test_cannot_freeze_without_stored_bn_statistics(model):
    with pytest.raises(ValueError, match="running statistics"):
        configure_training_mode(model, "frozen")


def test_buffer_audit_rejects_missing_or_nonfinite_data():
    with pytest.raises(ValueError, match="missing"):
        summarize_bn_changes({}, {})
    with pytest.raises(ValueError, match="nonfinite"):
        summarize_bn_changes({"bn.running_mean": torch.zeros(2)}, {"bn.running_mean": torch.tensor([0., float("nan")])})
