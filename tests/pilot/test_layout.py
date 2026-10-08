"""Regression checks for the relocated entrypoints, not a new training run."""

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("name", ["train_aasist_clean", "check_aasist_overfit", "check_aasist_batchnorm", "train_aasist_frozen_bn"])
def test_pilot_entrypoint_finds_project_root_after_move(name):
    path = ROOT / "experiments/pilot/scripts/aasist" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"layout_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.ROOT == ROOT
    assert (module.ROOT / "pyproject.toml").is_file()


def test_pilot_and_research_readmes_are_separate():
    assert (ROOT / "experiments/pilot/README.md").is_file()
    assert (ROOT / "experiments/research/README.md").is_file()
    assert not (ROOT / "scripts/train_aasist_pilot.py").exists()
    assert not (ROOT / "scripts/check_aasist_overfit.py").exists()
    assert not (ROOT / "experiments/pilot/scripts/train_aasist_clean.py").exists()
    assert not (ROOT / "experiments/pilot/scripts/check_aasist_overfit.py").exists()
    assert (ROOT / "experiments/pilot/scripts/rawnet2/README.md").is_file()
    assert not list((ROOT / "experiments/pilot/scripts/rawnet2").glob("*.py"))
