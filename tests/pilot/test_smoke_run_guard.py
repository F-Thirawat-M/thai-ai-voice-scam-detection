import importlib.util
from pathlib import Path

import pytest


@pytest.fixture
def trainer_module():
    path = Path(__file__).resolve().parents[2] / "experiments/pilot/scripts/aasist/train_aasist_clean.py"
    spec = importlib.util.spec_from_file_location("aasist_smoke_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("mode", [None, "train", "frozen"])
def test_existing_run_is_not_overwritten(trainer_module, tmp_path, monkeypatch, mode):
    module = trainer_module
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module.sys, "prefix", str(tmp_path / ".venv"))
    arguments = ["train", "--run-id", "existing"]
    if mode:
        arguments += ["--diagnostic-bn", mode]
    monkeypatch.setattr(module.sys, "argv", arguments)
    namespace = "aasist_bn_diagnostic" if mode else "aasist_clean_smoke"
    output = tmp_path / "results/pilot" / namespace / "existing"
    output.mkdir(parents=True)
    marker = output / "run.json"
    marker.write_text("original run", encoding="utf-8")
    with pytest.raises(FileExistsError, match="NEW"):
        module.main()
    assert marker.read_text(encoding="utf-8") == "original run"
    assert list(output.iterdir()) == [marker]


@pytest.mark.parametrize("arguments", [["--run-id", "../escape"], ["--run-id", "valid", "--max-batches", "3"],
                                      ["--run-id", "valid", "--diagnostic-bn", "invalid"],
                                      ["--run-id", "valid", "--diagnostic-bn", "frozen", "--max-batches", "2"]])
def test_invalid_run_arguments_rejected_before_loading_data(trainer_module, monkeypatch, arguments):
    monkeypatch.setattr(trainer_module.sys, "argv", ["train", *arguments])
    with pytest.raises(SystemExit) as error:
        trainer_module.main()
    assert error.value.code == 2
