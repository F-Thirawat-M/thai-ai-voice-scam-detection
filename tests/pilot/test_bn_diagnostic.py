import csv
import importlib.util
import json
from pathlib import Path

import pytest

from thai_spoof.pilot.pilot_data import file_sha256


@pytest.fixture
def driver():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("bn_driver_under_test", root / "experiments/pilot/scripts/aasist/check_aasist_batchnorm.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def arms(tmp_path):
    paths = []
    for mode, loss in [("train", 4.0), ("frozen", 0.8)]:
        path = tmp_path / mode
        path.mkdir()
        write(path / "training_log.json", {"sample_order_and_crops": [{"sample_id": str(i), "crop_start": i} for i in range(160)]})
        (path / "last.pt").write_bytes(b"toy checkpoint not a real trained model")
        with (path / "dev_scores.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "label", "stage", "spoof_logit", "bonafide_logit"])
            writer.writeheader()
            for stage in ["pretrained", "after_smoke"]:
                writer.writerows({"sample_id": str(i), "label": "bonafide" if i % 2 else "spoof", "stage": stage,
                                 "spoof_logit": 0.0, "bonafide_logit": 0.5} for i in range(40))
        run = {
            "run_id": mode, "status": "completed", "config": {"scope": "one_factor_bn_pilot_not_main_research",
            "batchnorm_mode": mode, "final_test_accessed": False, "lr": 1e-5},
            "samples_seen": 160, "input_counts": {"train": 160, "dev": 40}, "microbatches": 80, "optimizer_updates": 10,
            "exposures": {"spoof": 80, "bonafide": 80}, "canonical_report_sha256": "same", "manifest_sha256": "same",
            "initial_checkpoint_sha256": "same", "upstream_config_sha256": "same", "code_sha256": {"helper": "same"},
            "preparation_code_verification": {}, "environment": {"device": "cpu"}, "parameters_total": 20,
            "parameters_trainable": 20, "reload_max_abs_logit_error": 0.0, "pretrained_dev_loss": 1.0,
            "trained_dev_loss": loss, "batchnorm_audit": {"changed_buffer_count": 3 if mode == "train" else 0, "layer_count": 1},
            "training_log_sha256": file_sha256(path / "training_log.json"), "dev_scores_sha256": file_sha256(path / "dev_scores.csv"),
            "checkpoint_sha256": file_sha256(path / "last.pt"),
        }
        write(path / "run.json", run)
        paths.append(path)
    return paths


def test_comparison_accepts_only_controlled_pair(driver, arms):
    result = driver.compare_arms(*arms)
    assert result["controlled_checks_passed"] and not result["final_test_accessed"]
    assert result["frozen_minus_train_dev_loss"] == pytest.approx(-3.2)


@pytest.mark.parametrize("mutation", ["lr", "source", "frozen_buffers", "incomplete", "test", "checkpoint"])
def test_uncontrolled_or_tampered_pair_is_rejected(driver, arms, mutation):
    path = arms[1]
    run = json.loads((path / "run.json").read_text())
    if mutation == "lr":
        run["config"]["lr"] = 0.1
    elif mutation == "source":
        run["code_sha256"]["helper"] = "different"
    elif mutation == "frozen_buffers":
        run["batchnorm_audit"]["changed_buffer_count"] = 1
    elif mutation == "incomplete":
        run["optimizer_updates"] = 9
    elif mutation == "test":
        run["config"]["final_test_accessed"] = True
    else:
        (path / "last.pt").write_bytes(b"tampered")
    write(path / "run.json", run)
    with pytest.raises(ValueError):
        driver.compare_arms(*arms)


def test_train_crop_change_rejected_even_with_valid_file_hash(driver, arms):
    path = arms[1]
    log = json.loads((path / "training_log.json").read_text())
    log["sample_order_and_crops"][0]["crop_start"] += 1
    write(path / "training_log.json", log)
    run = json.loads((path / "run.json").read_text())
    run["training_log_sha256"] = file_sha256(path / "training_log.json")
    write(path / "run.json", run)
    with pytest.raises(ValueError, match="crop"):
        driver.compare_arms(*arms)


def test_existing_arm_stops_before_creating_pair_or_launching_training(driver, tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "ROOT", tmp_path)
    monkeypatch.setattr(driver.sys, "prefix", str(tmp_path / ".venv"))
    monkeypatch.setattr(driver.sys, "argv", ["bn", "--run-id", "existing"])
    base = tmp_path / "results/pilot/aasist_bn_diagnostic"
    arm = base / "existing_train"
    arm.mkdir(parents=True)
    marker = arm / "run.json"
    marker.write_text("original")
    with pytest.raises(FileExistsError, match="NEW"):
        driver.main()
    assert marker.read_text() == "original"
    assert not (base / "existing").exists()


@pytest.mark.parametrize("args", [["--run-id", "../escape"], ["--run-id", "ok", "--device", "invalid"]])
def test_invalid_driver_args_stop_before_reading_data(driver, monkeypatch, args):
    monkeypatch.setattr(driver.sys, "argv", ["bn", *args])
    with pytest.raises(SystemExit) as error:
        driver.main()
    assert error.value.code == 2
