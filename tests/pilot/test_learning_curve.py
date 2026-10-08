import copy

import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from thai_spoof.pilot.batchnorm import configure_training_mode, snapshot_bn_buffers
from thai_spoof.pilot.learning_curve import evaluate_split, train_frozen_epoch, select_best_trained_epoch


class Toy(nn.Module):
    def __init__(self, config=None):
        super().__init__()
        self.bn = nn.BatchNorm1d(2)
        self.drop = nn.Dropout(0.0)
        self.linear = nn.Linear(2, 2)

    def forward(self, x):
        hidden = self.drop(self.bn(x))
        return hidden, self.linear(hidden)


def fixture_data():
    x = torch.tensor([[0., 1.], [1., -1.], [2., 0.], [-1., 0.], [0., -2.], [2., 2.], [-2., 1.]])
    y = torch.tensor([0, 1, 1, 0, 0, 1, 0])
    return x, y, DataLoader(TensorDataset(x, y, torch.arange(7)), batch_size=2, shuffle=False)


def test_monitoring_restores_rng_and_does_not_update_bn():
    torch.manual_seed(42)
    model = Toy()
    _, _, loader = fixture_data()
    before_rng = torch.get_rng_state().clone()
    before_buffers = snapshot_bn_buffers(model)
    loss, scores = evaluate_split(model, loader, "cpu")
    assert torch.equal(before_rng, torch.get_rng_state())
    assert len(scores) == 7 and loss >= 0
    assert not model.training and not model.drop.training
    assert all(torch.equal(value, snapshot_bn_buffers(model)[name]) for name, value in before_buffers.items())


def test_accumulation_matches_full_group_including_short_tail():
    torch.manual_seed(42)
    model = Toy()
    reference = copy.deepcopy(model)
    x, y, loader = fixture_data()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.05)
    result = train_frozen_epoch(model, loader, optimizer, "cpu", accumulation=3)
    configure_training_mode(reference, "frozen")
    reference_optimizer = torch.optim.SGD(reference.parameters(), lr=0.05)
    for start, end in [(0, 6), (6, 7)]:
        reference_optimizer.zero_grad(set_to_none=True)
        _, logits = reference(x[start:end])
        nn.functional.cross_entropy(logits, y[start:end]).backward()
        nn.utils.clip_grad_norm_(reference.parameters(), 1.0)
        reference_optimizer.step()
    for parameter, expected in zip(model.parameters(), reference.parameters()):
        torch.testing.assert_close(parameter, expected, rtol=1e-5, atol=1e-6)
    assert result["samples_seen"] == 7 and len(result["updates"]) == 2
    assert result["sample_indices"] == list(range(7))
    assert result["batchnorm_audit"]["changed_buffer_count"] == 0


def test_next_epoch_restores_train_dropout_and_frozen_bn_after_evaluation():
    torch.manual_seed(42)
    model = Toy()
    _, _, loader = fixture_data()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    original = snapshot_bn_buffers(model)
    for _ in range(3):
        evaluate_split(model, loader, "cpu")
        stats = train_frozen_epoch(model, loader, optimizer, "cpu", accumulation=3)
        assert model.training and model.drop.training and not model.bn.training
        assert stats["batchnorm_audit"]["changed_buffer_count"] == 0
    assert all(torch.equal(value, snapshot_bn_buffers(model)[name]) for name, value in original.items())


def test_best_epoch_uses_dev_only_excludes_pretrained_and_breaks_ties_early():
    history = [{"epoch": 0, "dev_loss": 0.1, "train_evaluation_loss": 9.0},
               {"epoch": 1, "dev_loss": 0.3, "train_evaluation_loss": 0.9},
               {"epoch": 2, "dev_loss": 0.2, "train_evaluation_loss": 0.8},
               {"epoch": 3, "dev_loss": 0.2, "train_evaluation_loss": 0.1}]
    assert select_best_trained_epoch(history) == 2


@pytest.mark.parametrize("history", [[], [{"epoch": 0, "dev_loss": 1.}],
                                     [{"epoch": 0, "dev_loss": 1.}, {"epoch": 2, "dev_loss": 0.5}],
                                     [{"epoch": 0, "dev_loss": 1.}, {"epoch": 1, "dev_loss": float("nan")}],
                                     [{"epoch": 0, "dev_loss": 1.}, {"epoch": 1, "dev_loss": -0.1}]])
def test_invalid_epoch_history_rejected(history):
    with pytest.raises(ValueError):
        select_best_trained_epoch(history)


@pytest.mark.parametrize("accumulation", [0, True, 1.5])
def test_invalid_accumulation_rejected_before_model_mode_changes(accumulation):
    model = Toy().eval()
    _, _, loader = fixture_data()
    with pytest.raises(ValueError):
        train_frozen_epoch(model, loader, torch.optim.SGD(model.parameters(), lr=0.01), "cpu", accumulation=accumulation)
    assert not model.training


def test_nonfinite_training_logits_rejected():
    model = Toy()
    x, y, _ = fixture_data()
    x[0, 0] = float("nan")
    loader = DataLoader(TensorDataset(x, y, torch.arange(7)), batch_size=2)
    with pytest.raises(RuntimeError, match="invalid Train logits"):
        train_frozen_epoch(model, loader, torch.optim.SGD(model.parameters(), lr=0.01), "cpu")
