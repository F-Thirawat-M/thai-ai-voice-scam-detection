"""Run exactly two fresh Clean epochs changing BN mode only; no Test or EER."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from thai_spoof.pilot.pilot_data import file_sha256


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def compare_arms(train_dir: Path, frozen_dir: Path) -> dict:
    runs = [json.loads((path / "run.json").read_text(encoding="utf-8")) for path in [train_dir, frozen_dir]]
    for run, mode in zip(runs, ["train", "frozen"]):
        if (run["status"] != "completed" or run["config"]["batchnorm_mode"] != mode
                or run["config"]["scope"] != "one_factor_bn_pilot_not_main_research"
                or run["config"]["final_test_accessed"] or run["samples_seen"] != 160
                or run["input_counts"] != {"train": 160, "dev": 40}
                or run["microbatches"] != 80 or run["optimizer_updates"] != 10
                or run["exposures"] != {"spoof": 80, "bonafide": 80}):
            raise ValueError("incomplete or invalid BN diagnostic arm")
    a, b = runs
    for key in ["canonical_report_sha256", "manifest_sha256", "initial_checkpoint_sha256",
                "upstream_config_sha256", "code_sha256", "preparation_code_verification",
                "environment", "parameters_total", "parameters_trainable"]:
        if a[key] != b[key]:
            raise ValueError(f"uncontrolled difference between arms: {key}")
    configs = [{key: value for key, value in run["config"].items() if key != "batchnorm_mode"} for run in runs]
    if configs[0] != configs[1]:
        raise ValueError("recipe differed beyond BatchNorm mode")
    logs, initial_scores = [], []
    for path, run in zip([train_dir, frozen_dir], runs):
        for name, key in [("training_log.json", "training_log_sha256"), ("dev_scores.csv", "dev_scores_sha256"),
                          ("last.pt", "checkpoint_sha256")]:
            if file_sha256(path / name) != run[key]:
                raise ValueError(f"arm artifact hash mismatch: {name}")
        log = json.loads((path / "training_log.json").read_text(encoding="utf-8"))
        logs.append(log["sample_order_and_crops"])
        with (path / "dev_scores.csv").open(encoding="utf-8", newline="") as handle:
            scores = list(csv.DictReader(handle))
        before = [score for score in scores if score["stage"] == "pretrained"]
        if len(before) != 40 or len(scores) != 80:
            raise ValueError("wrong Dev score counts")
        initial_scores.append(before)
        if run["reload_max_abs_logit_error"] > 1e-5:
            raise ValueError("reload diagnostic failed")
    if logs[0] != logs[1] or len(logs[0]) != 160:
        raise ValueError("Train order/crop changed between arms")
    if [(r["sample_id"], r["label"]) for r in initial_scores[0]] != [(r["sample_id"], r["label"]) for r in initial_scores[1]]:
        raise ValueError("Dev order/labels changed")
    logits = [np.array([[float(r["spoof_logit"]), float(r["bonafide_logit"])] for r in scores]) for scores in initial_scores]
    np.testing.assert_allclose(logits[0], logits[1], rtol=1e-5, atol=1e-5)
    if a["batchnorm_audit"]["changed_buffer_count"] <= 0 or b["batchnorm_audit"]["changed_buffer_count"] != 0:
        raise ValueError("BN treatment audit failed")
    if a["batchnorm_audit"]["layer_count"] != b["batchnorm_audit"]["layer_count"]:
        raise ValueError("BN layer counts differ")
    delta = b["trained_dev_loss"] - a["trained_dev_loss"]
    if not np.isfinite([a["trained_dev_loss"], b["trained_dev_loss"], delta]).all():
        raise ValueError("nonfinite comparison")
    return {
        "scope": "single_seed_one_epoch_BN_mode_diagnostic_not_Test_or_final_recipe",
        "controlled_checks_passed": True, "final_test_accessed": False,
        "same_train_order_and_crops": True, "same_initial_dev_logits": True,
        "pretrained_dev_loss": a["pretrained_dev_loss"],
        "train_bn_dev_loss": a["trained_dev_loss"], "frozen_bn_dev_loss": b["trained_dev_loss"],
        "frozen_minus_train_dev_loss": delta,
        "bn_buffer_changes": {mode: run["batchnorm_audit"] for mode, run in zip(["train", "frozen"], runs)},
        "arms": {mode: {"run_id": run["run_id"], "run_json_sha256": file_sha256(path / "run.json")}
                 for mode, run, path in zip(["train", "frozen"], runs, [train_dir, frozen_dir])},
        "limitations": ["one seed and one epoch; Dev used for recipe development",
                        "frozen BN changes Train normalization as well as running-buffer updates",
                        "dropout remains enabled and BN affine parameters remain trainable",
                        "no claim of best hyperparameters, Test accuracy, EER or Clean/Mixed comparison"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="fresh pair name, max 60 characters")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,59}", args.run_id):
        parser.error("use 1-60 letters/numbers/hyphens/underscores")
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        parser.error("use the project's main .venv Python")
    base = ROOT / "results/pilot/aasist_bn_diagnostic"
    output = base / args.run_id
    arm_dirs = [base / f"{args.run_id}_{mode}" for mode in ["train", "frozen"]]
    if any(path.exists() for path in [output, *arm_dirs]):
        raise FileExistsError("existing pair/arm; choose NEW run-id; never overwrite")
    state = {"status": "running", "run_id": args.run_id, "started_utc": datetime.now(timezone.utc).isoformat(),
             "scope": "two_Clean_epochs_one_factor_BN_mode_no_Test", "final_test_accessed": False,
             "driver_sha256": file_sha256(Path(__file__)),
             "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "run.json", state)
    try:
        for mode, path in zip(["train", "frozen"], arm_dirs):
            print(f"\nBN diagnostic arm: {mode}; fresh pretrained, full Train 160 / Dev 40.", flush=True)
            subprocess.run([sys.executable, "-u", str(ROOT / "experiments/pilot/scripts/aasist/train_aasist_clean.py"),
                            "--run-id", path.name, "--device", args.device, "--diagnostic-bn", mode],
                           cwd=ROOT, check=True)
        comparison = compare_arms(*arm_dirs)
        write_json(output / "comparison.json", comparison)
        state.update({"status": "completed", "controlled_checks_passed": True,
                      "comparison_sha256": file_sha256(output / "comparison.json")})
        write_json(output / "run.json", state)
        print(f"\nPretrained Dev loss: {comparison['pretrained_dev_loss']:.6f}", flush=True)
        print(f"Train BN: {comparison['train_bn_dev_loss']:.6f}; frozen BN: {comparison['frozen_bn_dev_loss']:.6f}", flush=True)
        print(f"Verified pair saved to {output}. Diagnostic only; no Test/EER.", flush=True)
    except BaseException as error:
        state.update({"status": "failed", "error": f"{type(error).__name__}: {error}"})
        write_json(output / "run.json", state)
        raise


if __name__ == "__main__":
    main()
