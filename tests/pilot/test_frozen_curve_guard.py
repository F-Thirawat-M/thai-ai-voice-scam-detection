import importlib.util
from pathlib import Path

import pytest
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from thai_spoof.pilot.learning_curve import evaluate_split


@pytest.fixture
def driver():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("frozen_curve_under_test", root / "experiments/pilot/scripts/aasist/train_aasist_frozen_bn.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_run_not_overwritten(driver, tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "ROOT", tmp_path)
    monkeypatch.setattr(driver.sys, "prefix", str(tmp_path / ".venv"))
    monkeypatch.setattr(driver.sys, "argv", ["curve", "--run-id", "existing"])
    output = tmp_path / "results/pilot/aasist_frozen_bn_curve/existing"
    output.mkdir(parents=True)
    marker = output / "run.json"
    marker.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError, match="NEW"):
        driver.main()
    assert marker.read_text() == "original" and list(output.iterdir()) == [marker]


@pytest.mark.parametrize("args", [["--run-id", "../escape"], ["--run-id", "ok", "--epochs", "10"],
                                  ["--run-id", "ok", "--device", "invalid"]])
def test_invalid_or_unbounded_arguments_rejected(driver, monkeypatch, args):
    monkeypatch.setattr(driver.sys, "argv", ["curve", *args])
    with pytest.raises(SystemExit) as error:
        driver.main()
    assert error.value.code == 2


class ReloadToy(nn.Module):
    def __init__(self, config=None):
        super().__init__()
        self.linear = nn.Linear(2, 2)

    def forward(self, x):
        return x, self.linear(x)


def test_fresh_model_reload_does_not_consume_training_rng(driver, tmp_path):
    torch.manual_seed(42)
    model = ReloadToy()
    loader = DataLoader(TensorDataset(torch.ones(4, 2), torch.tensor([0, 1, 0, 1]), torch.arange(4)), batch_size=2)
    _, scores = evaluate_split(model, loader, "cpu")
    checkpoint = tmp_path / "epoch.pt"
    torch.save({"model": model.state_dict()}, checkpoint)
    rng = torch.get_rng_state().clone()
    assert driver.verify_reload(model, checkpoint, {}, loader, torch.device("cpu"), scores) == 0.0
    assert torch.equal(rng, torch.get_rng_state())
