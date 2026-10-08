import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from thai_spoof.pilot.pilot_data import file_sha256
from thai_spoof.pilot.seed_stability import CODE_PATHS, TRAINER, SEED_ARGUMENT, SEED_GUARD, audit_source, summarize_runs


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def fixture_runs(tmp_path):
    root = tmp_path / "root"
    legacy = "    seed = 42\n"
    current = SEED_ARGUMENT + SEED_GUARD + "    seed = args.seed\n"
    for name in CODE_PATHS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(current if name == TRAINER else "x = 1\n", encoding="utf-8")
    fixed = root / "checkpoints/aasist/AASIST.pth"
    fixed.parent.mkdir(parents=True, exist_ok=True)
    fixed.write_bytes(b"toy weights")
    upstream = root / "external/aasist/config/AASIST.conf"
    write(upstream, {})
    paths = []
    for seed, last in [(42, 0.3), (43, 0.4), (44, 0.5)]:
        path = root / "runs" / str(seed)
        path.mkdir(parents=True)
        history = [{"epoch": 0, "dev_loss": 1.5, "train_evaluation_loss": 1.7}]
        for epoch, dev in [(1, 1.0), (2, 0.6), (3, last)]:
            checkpoint = path / f"epoch_{epoch:03d}.pt"
            checkpoint.write_bytes(f"toy seed {seed} epoch {epoch}".encode())
            history.append({"epoch": epoch, "dev_loss": dev, "train_evaluation_loss": dev + 0.2,
                            "checkpoint": checkpoint.name, "checkpoint_sha256": file_sha256(checkpoint), "reload_max_abs_logit_error": 0.0})
        write(path / "learning_curve.json", {"history": history})
        write(path / "selection.json", {"best_epoch": 3, "checkpoint": "epoch_003.pt",
              "checkpoint_sha256": history[3]["checkpoint_sha256"], "dev_loss": last})
        order = [{"sample_id": str(i), "label": "spoof" if i % 2 else "bonafide", "crop_start": seed} for i in range(160)]
        write(path / "training_log.json", {"epochs": [{"epoch": epoch, "sample_order_and_crops": order, "samples_seen": 160,
              "updates": [{}] * 10, "microbatches": [{}] * 80, "batchnorm_audit": {"changed_buffer_count": 0}} for epoch in range(1, 4)]})
        with (path / "scores.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["epoch", "split", "sample_id", "label", "spoof_logit", "bonafide_logit"])
            writer.writeheader()
            for epoch in range(4):
                for split, count in [("train", 160), ("dev", 40)]:
                    writer.writerows({"epoch": epoch, "split": split, "sample_id": str(i), "label": "spoof" if i % 2 else "bonafide",
                                      "spoof_logit": 0.0, "bonafide_logit": 0.5} for i in range(count))
        (path / "loss_curve.png").write_bytes(b"toy image artifact")
        code = {name: file_sha256(root / name) for name in CODE_PATHS}
        if seed == 42:
            code[TRAINER] = hashlib.sha256(legacy.encode()).hexdigest()
        run = {"status": "completed", "run_id": str(seed), "config": {"seed": seed, "epochs": 3, "batchnorm_mode": "frozen",
               "scope": "bounded_three_epoch_Frozen_BN_pilot_not_main_research", "final_test_accessed": False, "learning_rate": 1e-5},
               "epochs_completed": 3, "optimizer_updates": 30, "clip_exposures": 480, "unique_Train_clips": 160,
               "input_counts": {"train": 160, "dev": 40}, "batchnorm_audit": {"changed_buffer_count": 0},
               "parameters_total": 10, "parameters_trainable": 10, "code_sha256": code,
               "artifact_sha256": {name: file_sha256(path / name) for name in ["learning_curve.json", "selection.json", "scores.csv", "training_log.json", "loss_curve.png"]},
               "history": history, "best_epoch": 3, "manifest_sha256": "same", "canonical_report_sha256": "same",
               "initial_checkpoint_sha256": file_sha256(fixed), "upstream_config_sha256": file_sha256(upstream), "environment": {"device": "cpu"}}
        write(path / "run.json", run)
        paths.append(path)
    return root, paths


def test_all_three_seeds_reported_with_sample_std_not_best_seed(fixture_runs):
    root, paths = fixture_runs
    result = summarize_runs(paths, root)
    assert result["seeds"] == [42, 43, 44] and len(result["runs"]) == 3
    assert result["epoch_statistics"][3]["dev_loss"]["mean"] == pytest.approx(0.4)
    assert result["epoch_statistics"][3]["dev_loss"]["sample_std_ddof1"] == pytest.approx(0.1)
    assert not result["final_test_accessed"] and result["controls_passed"]
    assert "best_seed" not in result


@pytest.mark.parametrize("mutation", ["seed", "recipe", "weights", "status", "test", "checkpoint", "helper_source", "trainer_source"])
def test_incompatible_or_tampered_runs_rejected(fixture_runs, mutation):
    root, paths = fixture_runs
    path = paths[1]
    run = json.loads((path / "run.json").read_text())
    if mutation == "seed": run["config"]["seed"] = 45
    elif mutation == "recipe": run["config"]["learning_rate"] = 0.1
    elif mutation == "weights": run["initial_checkpoint_sha256"] = "different"
    elif mutation == "status": run["status"] = "failed"
    elif mutation == "test": run["config"]["final_test_accessed"] = True
    elif mutation == "checkpoint": (path / "epoch_003.pt").write_bytes(b"tampered")
    elif mutation == "helper_source": (root / "src/thai_spoof/pilot/learning_curve.py").write_text("x = 2\n")
    else: (root / TRAINER).write_text((root / TRAINER).read_text() + "# additional change\n")
    write(path / "run.json", run)
    with pytest.raises(ValueError): summarize_runs(paths, root)


def test_approved_legacy_seed_cli_and_checkout_newlines_only(fixture_runs):
    root, paths = fixture_runs
    run = json.loads((paths[0] / "run.json").read_text())
    assert audit_source(root, run)[TRAINER] == "exact_seed_CLI_extension_and_checkout_newlines_only"
    path = root / TRAINER
    path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    assert audit_source(root, run)[TRAINER] == "exact_seed_CLI_extension_and_checkout_newlines_only"
    path.write_bytes(path.read_bytes().replace(b"args.seed", b"args.seed + 1", 1))
    with pytest.raises(ValueError): audit_source(root, run)


@pytest.mark.parametrize("indices", [[0, 1], [0, 0, 2], [2, 1, 0]])
def test_subset_duplicate_or_wrong_seed_order_rejected(fixture_runs, indices):
    root, paths = fixture_runs
    with pytest.raises(ValueError): summarize_runs([paths[i] for i in indices], root)


@pytest.fixture
def driver():
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("seed_driver_test", root / "experiments/pilot/scripts/aasist/check_aasist_seed_stability.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_existing_child_run_stops_before_training(driver, tmp_path, monkeypatch):
    monkeypatch.setattr(driver, "ROOT", tmp_path)
    monkeypatch.setattr(driver.sys, "prefix", str(tmp_path / ".venv"))
    monkeypatch.setattr(driver.sys, "argv", ["suite", "--run-id", "existing"])
    arm = tmp_path / "results/pilot/aasist_frozen_bn_curve/existing_seed44"
    arm.mkdir(parents=True)
    marker = arm / "run.json"
    marker.write_text("original")
    with pytest.raises(FileExistsError, match="NEW"): driver.main()
    assert marker.read_text() == "original"
    assert not (tmp_path / "results/pilot/aasist_seed_stability/existing").exists()


@pytest.mark.parametrize("args", [["--run-id", "../escape"], ["--run-id", "ok", "--reference-run", "../escape"],
                                  ["--run-id", "ok", "--seeds", "42,43,44,45"]])
def test_invalid_or_expanded_budget_rejected(driver, monkeypatch, args):
    monkeypatch.setattr(driver.sys, "argv", ["suite", *args])
    with pytest.raises(SystemExit) as error: driver.main()
    assert error.value.code == 2
