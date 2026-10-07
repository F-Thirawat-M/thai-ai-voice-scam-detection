import importlib.util
import json
from pathlib import Path

import pytest


@pytest.fixture
def overfit_script(tmp_path, monkeypatch):
    path = Path(__file__).resolve().parents[2] / "scripts/check_aasist_overfit.py"
    spec = importlib.util.spec_from_file_location("overfit_script_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module.sys, "prefix", str(tmp_path / ".venv"))
    monkeypatch.setattr(module.sys, "argv", ["overfit", "--run-id", "guard"])
    return module


def test_existing_overfit_run_is_not_overwritten(overfit_script, tmp_path):
    output = tmp_path / "results/cvtts/aasist_overfit_check/guard"
    output.mkdir(parents=True)
    marker = output / "run.json"
    marker.write_text("original", encoding="utf-8")
    with pytest.raises(FileExistsError, match="NEW"):
        overfit_script.main()
    assert marker.read_text(encoding="utf-8") == "original"
    assert list(output.iterdir()) == [marker]


@pytest.mark.parametrize("arguments", [["--run-id", "../escape"], ["--run-id", "ok", "--max-updates", "999"]])
def test_invalid_arguments_rejected(overfit_script, monkeypatch, arguments):
    monkeypatch.setattr(overfit_script.sys, "argv", ["overfit", *arguments])
    with pytest.raises(SystemExit) as error:
        overfit_script.main()
    assert error.value.code == 2


def test_data_entry_point_requests_train_only(overfit_script, tmp_path, monkeypatch):
    report = tmp_path / "data/processed/cvtts/pilot_v1/qc/canonical_audio/wayu_pilot_clean16k_v1.json"
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps({"audio_policy": "mono16k_float_fullclip_v1", "preparation_code_sha256": {},
                                  "manifest_sha256": {"wayu_pilot_train_clean16k.csv": "expected"}}), encoding="utf-8")
    calls = []
    class StopBeforeGPU(Exception):
        pass
    def loader(root, split, digest):
        calls.append((split, digest))
        raise StopBeforeGPU()
    monkeypatch.setattr(overfit_script, "load_pilot_split", loader)
    with pytest.raises(StopBeforeGPU):
        overfit_script.main()
    assert calls == [("train", "expected")]
    assert not (tmp_path / "results").exists()
