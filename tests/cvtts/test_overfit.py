import copy

import numpy as np
import pytest
import torch
from torch import nn

from thai_spoof.cvtts.overfit import evaluate_fixed, fit_fixed_batch, select_train_pairs


def paired_rows(count=5):
    return [{"sample_id": f"{i}_{label}", "source_sample_id": str(i), "source_text_key": f"text {i}",
             "split": "train", "label": label} for i in range(count) for label in ["bonafide", "spoof"]]


def test_pair_selection_is_balanced_seeded_and_independent_of_row_order():
    rows = paired_rows()
    selected = select_train_pairs(rows)
    assert len(selected) == 4
    assert [rows[i]["label"] for i in selected] == ["bonafide", "spoof"] * 2
    reverse = list(reversed(rows))
    assert [rows[i]["sample_id"] for i in selected] == [reverse[i]["sample_id"] for i in select_train_pairs(reverse)]
    assert select_train_pairs(rows) == selected


@pytest.mark.parametrize("mutation", ["dev", "duplicate", "unpaired", "text"])
def test_invalid_pairs_rejected(mutation):
    rows = paired_rows()
    if mutation == "dev":
        rows[0]["split"] = "dev"
    elif mutation == "duplicate":
        rows.append(dict(rows[0]))
    elif mutation == "unpaired":
        rows.pop()
    else:
        rows[0]["source_text_key"] = "different"
    with pytest.raises(ValueError):
        select_train_pairs(rows)


@pytest.mark.parametrize("pairs", [True, 0, 1.5, 20])
def test_invalid_pair_count_rejected(pairs):
    with pytest.raises(ValueError):
        select_train_pairs(paired_rows(), pairs=pairs)


class Toy(nn.Module):
    def __init__(self):
        super().__init__()
        self.bn = nn.BatchNorm1d(2)
        self.drop = nn.Dropout(0.5)
        self.linear = nn.Linear(2, 2)
        nn.init.zeros_(self.linear.weight)
        nn.init.zeros_(self.linear.bias)

    def forward(self, x):
        h = self.drop(self.bn(x))
        return h, self.linear(h)


def batch():
    return torch.tensor([[-1000., 0], [1000., 0], [-1000., 0], [1000., 0]]), torch.tensor([0, 1, 0, 1])


def test_fixed_batch_learns_with_autograd_but_bn_and_dropout_stay_frozen(tmp_path):
    model = Toy()
    x, y = batch()
    original_buffers = {name: b.clone() for name, b in model.named_buffers()}
    history, optimizer, passed = fit_fixed_batch(model, x, y, max_updates=40)
    assert passed and history[-1]["update"] >= 20
    assert history[-1]["loss"] < history[0]["loss"] and history[-1]["accuracy"] == 1
    assert not model.training and not model.drop.training and not model.bn.training
    assert all(torch.equal(b, original_buffers[name]) for name, b in model.named_buffers())
    assert model.linear.weight.abs().sum() > 0
    path = tmp_path / "check.pt"
    torch.save({"model": model.state_dict(), "optimizer": optimizer.state_dict()}, path)
    fresh = Toy()
    fresh.load_state_dict(torch.load(path, weights_only=True)["model"])
    np.testing.assert_allclose(evaluate_fixed(model, x, y)["logits"], evaluate_fixed(fresh, x, y)["logits"], rtol=1e-5, atol=1e-5)


def test_accumulation_matches_full_subset_weight_even_with_uneven_microbatch():
    one = Toy()
    other = copy.deepcopy(one)
    x, y = batch()
    fit_fixed_batch(one, x, y, max_updates=20, microbatch=3)
    fit_fixed_batch(other, x, y, max_updates=20, microbatch=4)
    for a, b in zip(one.parameters(), other.parameters()):
        torch.testing.assert_close(a, b, rtol=1e-4, atol=1e-6)


@pytest.mark.parametrize("invalid", ["one_label", "nan", "shape", "dtype"])
def test_invalid_fixed_batch_rejected(invalid):
    x, y = batch()
    if invalid == "one_label":
        y.zero_()
    elif invalid == "nan":
        x[0, 0] = float("nan")
    elif invalid == "shape":
        y = y[:2]
    else:
        y = y.float()
    with pytest.raises(ValueError):
        fit_fixed_batch(Toy(), x, y)


def test_max_budget_and_frozen_parameter_rejected():
    x, y = batch()
    with pytest.raises(ValueError, match="budget"):
        fit_fixed_batch(Toy(), x, y, max_updates=201)
    model = Toy()
    model.linear.weight.requires_grad_(False)
    with pytest.raises(ValueError, match="all parameters"):
        fit_fixed_batch(model, x, y)
