import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def trainer_module():
    path = Path(__file__).resolve().parents[2] / "scripts/train_aasist_pilot.py"
    spec = importlib.util.spec_from_file_location("aasist_smoke_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_run_is_not_overwritten(trainer_module, tmp_path, monkeypatch):
    module = trainer_module
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module.sys, "prefix", str(tmp_path / ".venv"))
    monkeypatch.setattr(module.sys, "argv", ["train", "--run-id", "existing"])
    output = tmp_path / "results/cvtts/aasist_clean_smoke/existing"
    output.mkdir(parents=True)
    marker = output / "run.json"
    marker.write_text("original run", encoding="utf-8")
    with pytest.raises(FileExistsError, match="NEW"):
        module.main()
    assert marker.read_text(encoding="utf-8") == "original run"
    assert list(output.iterdir()) == [marker]


@pytest.mark.parametrize("arguments", [["--run-id", "../escape"], ["--run-id", "valid", "--max-batches", "3"]])
def test_invalid_run_arguments_rejected_before_loading_data(trainer_module, monkeypatch, arguments):
    monkeypatch.setattr(trainer_module.sys, "argv", ["train", *arguments])
    with pytest.raises(SystemExit) as error:
        trainer_module.main()
    assert error.value.code == 2
