"""Audit/report three predeclared seeds on the same pilot split; not Test stats."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from ..cvtts.provenance import verify_preparation_code
from .pilot_data import file_sha256


TRAINER = "experiments/pilot/scripts/aasist/train_aasist_frozen_bn.py"
CODE_PATHS = {TRAINER, "src/thai_spoof/pilot/learning_curve.py", "src/thai_spoof/pilot/batchnorm.py",
              "src/thai_spoof/pilot/pilot_data.py", "src/thai_spoof/cvtts/windows.py",
              "src/thai_spoof/cvtts/provenance.py", "src/thai_spoof/aasist/detector.py",
              "src/thai_spoof/aasist/config.json", "external/aasist/models/AASIST.py", "external/aasist/data_utils.py"}
SEED_ARGUMENT = '    parser.add_argument("--seed", type=int, default=42, help="seed for fixed crop, shuffle and dropout (default: 42)")\n'
SEED_GUARD = '    if not 0 <= args.seed <= 2**32 - 2:\n        parser.error("seed must be between 0 and 4294967294")\n'


def audit_source(root: Path, run: dict) -> dict:
    """Permit exact/LF checkout matches; seed 42 may precede the exact CLI extension."""
    if set(run["code_sha256"]) != CODE_PATHS:
        raise ValueError("unexpected source-code manifest")
    report = {}
    for name, expected in run["code_sha256"].items():
        path = root / name
        try:
            report[name] = verify_preparation_code(path, expected)["verification"]
        except ValueError:
            if name != TRAINER or run["config"]["seed"] != 42:
                raise
            source = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
            if source.count(SEED_ARGUMENT) != 1 or source.count(SEED_GUARD) != 1 or source.count("    seed = args.seed\n") != 1:
                raise ValueError("not the approved seed-CLI source extension")
            legacy = source.replace(SEED_ARGUMENT, "").replace(SEED_GUARD, "").replace("    seed = args.seed\n", "    seed = 42\n")
            permitted = {hashlib.sha256(legacy.encode()).hexdigest(), hashlib.sha256(legacy.replace("\n", "\r\n").encode()).hexdigest()}
            if expected not in permitted:
                raise ValueError("legacy trainer changed beyond the approved seed CLI")
            report[name] = "exact_seed_CLI_extension_and_checkout_newlines_only"
    return report


def validate_run(path: Path, root: Path, expected_seed: int):
    run = json.loads((path / "run.json").read_text(encoding="utf-8"))
    if (run["status"] != "completed" or run["config"]["seed"] != expected_seed
            or run["config"]["scope"] != "bounded_three_epoch_Frozen_BN_pilot_not_main_research"
            or run["config"]["batchnorm_mode"] != "frozen" or run["config"]["final_test_accessed"]
            or run["epochs_completed"] != 3 or run["config"]["epochs"] != 3
            or run["optimizer_updates"] != 30 or run["clip_exposures"] != 480 or run["unique_Train_clips"] != 160
            or run["input_counts"] != {"train": 160, "dev": 40} or run["batchnorm_audit"]["changed_buffer_count"] != 0
            or run["parameters_trainable"] != run["parameters_total"]):
        raise ValueError("invalid/incomplete Frozen-BN seed run")
    audit = audit_source(root, run)
    for key, name in [("initial_checkpoint_sha256", "checkpoints/aasist/AASIST.pth"),
                      ("upstream_config_sha256", "external/aasist/config/AASIST.conf")]:
        if file_sha256(root / name) != run[key]:
            raise ValueError(f"current initial asset differs: {key}")
    artifact_names = {"scores.csv", "training_log.json", "learning_curve.json", "selection.json", "loss_curve.png"}
    if set(run["artifact_sha256"]) != artifact_names:
        raise ValueError("unexpected artifact manifest")
    for name, expected in run["artifact_sha256"].items():
        if file_sha256(path / name) != expected:
            raise ValueError(f"artifact hash mismatch: {name}")
    history = run["history"]
    if len(history) != 4 or [row["epoch"] for row in history] != [0, 1, 2, 3]:
        raise ValueError("incomplete epoch history")
    for row in history:
        if not np.isfinite([row["dev_loss"], row["train_evaluation_loss"]]).all() or min(row["dev_loss"], row["train_evaluation_loss"]) < 0:
            raise ValueError("invalid loss in history")
    for epoch, row in enumerate(history[1:], start=1):
        if row["checkpoint"] != f"epoch_{epoch:03d}.pt" or file_sha256(path / row["checkpoint"]) != row["checkpoint_sha256"]:
            raise ValueError("checkpoint hash/name mismatch")
        if not np.isfinite(row["reload_max_abs_logit_error"]) or row["reload_max_abs_logit_error"] > 1e-5:
            raise ValueError("reload check failed")
    if json.loads((path / "learning_curve.json").read_text())["history"] != history:
        raise ValueError("curve/run history mismatch")
    selected = min(history[1:], key=lambda row: (row["dev_loss"], row["epoch"]))
    selection = json.loads((path / "selection.json").read_text())
    if (run["best_epoch"] != selected["epoch"] or selection["best_epoch"] != selected["epoch"] or selection["checkpoint"] != selected["checkpoint"]
            or selection["checkpoint_sha256"] != selected["checkpoint_sha256"] or selection["dev_loss"] != selected["dev_loss"]):
        raise ValueError("selection did not use Dev correctly")
    logs = json.loads((path / "training_log.json").read_text())["epochs"]
    if len(logs) != 3 or [log["epoch"] for log in logs] != [1, 2, 3]:
        raise ValueError("incomplete training logs")
    windows = None
    for log in logs:
        order = log["sample_order_and_crops"]
        if (log["samples_seen"] != 160 or len(log["updates"]) != 10 or len(log["microbatches"]) != 80
                or len(order) != 160 or len({row["sample_id"] for row in order}) != 160
                or {label: sum(row["label"] == label for row in order) for label in ["spoof", "bonafide"]} != {"spoof": 80, "bonafide": 80}
                or log["batchnorm_audit"]["changed_buffer_count"] != 0):
            raise ValueError("invalid Train coverage/BN audit")
        current = {row["sample_id"]: row["crop_start"] for row in order}
        if windows is not None and windows != current:
            raise ValueError("Train crop changed within a seed")
        windows = current
    with (path / "scores.csv").open(encoding="utf-8", newline="") as handle:
        scores = list(csv.DictReader(handle))
    if len(scores) != 800:
        raise ValueError("wrong score counts")
    baseline = [row for row in scores if row["split"] == "dev" and row["epoch"] == "0"]
    if len(baseline) != 40 or len({row["sample_id"] for row in baseline}) != 40:
        raise ValueError("wrong baseline Dev rows")
    return run, logs, baseline, audit


def summarize_runs(paths: list[Path], root: Path) -> dict:
    if len(paths) != 3 or len({path.resolve() for path in paths}) != 3:
        raise ValueError("exactly three distinct runs for seeds 42/43/44 are required")
    audited = [validate_run(path, root, seed) for path, seed in zip(paths, [42, 43, 44])]
    runs = [item[0] for item in audited]
    reference = runs[0]
    for run in runs[1:]:
        if {key: value for key, value in run["config"].items() if key != "seed"} != {key: value for key, value in reference["config"].items() if key != "seed"}:
            raise ValueError("recipe differs beyond seed")
        for key in ["manifest_sha256", "canonical_report_sha256", "initial_checkpoint_sha256", "upstream_config_sha256",
                    "environment", "parameters_total", "parameters_trainable"]:
            if run[key] != reference[key]:
                raise ValueError(f"uncontrolled difference: {key}")
    for key, relative_path in [("initial_checkpoint_sha256", "checkpoints/aasist/AASIST.pth"),
                               ("upstream_config_sha256", "external/aasist/config/AASIST.conf")]:
        if file_sha256(root / relative_path) != reference[key]:
            raise ValueError(f"current initial asset differs: {key}")
    for _, logs, baseline, _ in audited[1:]:
        if {row["sample_id"] for row in logs[0]["sample_order_and_crops"]} != {row["sample_id"] for row in audited[0][1][0]["sample_order_and_crops"]}:
            raise ValueError("different Train clip set")
        if [(row["sample_id"], row["label"]) for row in baseline] != [(row["sample_id"], row["label"]) for row in audited[0][2]]:
            raise ValueError("different Dev clip set/order")
        values = lambda rows: np.array([[float(row["spoof_logit"]), float(row["bonafide_logit"])] for row in rows])
        a, b = values(baseline), values(audited[0][2])
        if not np.isfinite(a).all() or not np.isfinite(b).all():
            raise ValueError("nonfinite baseline logits")
        np.testing.assert_allclose(a, b, rtol=1e-5, atol=1e-5)
    stats = []
    for epoch in range(4):
        row = {"epoch": epoch, "seed_count": 3}
        for metric in ["train_evaluation_loss", "dev_loss"]:
            values = np.array([run["history"][epoch][metric] for run in runs])
            row[metric] = {"mean": float(values.mean()), "sample_std_ddof1": float(values.std(ddof=1)),
                           "minimum": float(values.min()), "maximum": float(values.max())}
        stats.append(row)
    return {"scope": "three_predeclared_seeds_same_pilot_split_not_Test_or_seed_selection", "seeds": [42, 43, 44],
            "controls_passed": True, "final_test_accessed": False, "same_train_clip_set": True, "same_initial_Dev_logits": True,
            "source_compatibility": "only seed CLI extension and CRLF_to_LF checkout changes permitted",
            "epoch_statistics": stats, "std_definition": "sample standard deviation with ddof=1 across three training seeds; not CI",
            "runs": [{"seed": run["config"]["seed"], "run_id": run["run_id"], "run_json_sha256": file_sha256(path / "run.json"),
                      "history": run["history"], "best_epoch_by_Dev": run["best_epoch"], "source_audit": audit,
                      "epoch3_better_than_pretrained_Dev": run["history"][3]["dev_loss"] < run["history"][0]["dev_loss"],
                      "Dev_nonincreasing_over_three_epochs": all(b["dev_loss"] <= a["dev_loss"] for a, b in zip(run["history"], run["history"][1:]))}
                     for path, (run, _, _, audit) in zip(paths, audited)],
            "limitations": ["same small split, one generator, only three seeds; Dev used for recipe development",
                            "seed changes Train crops, shuffle, dropout; cohort/Dev windows unchanged",
                            "seed 42 reused from earlier run; audited minimal seed CLI extension",
                            "report all seeds; no best-seed selection or Test/EER/generalization claim"]}


def plot_seed_curves(summary: dict, output: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.7), sharey=True)
    for ax, metric, title in zip(axes, ["train_evaluation_loss", "dev_loss"], ["Train (eval; each seed's fixed crop)", "Dev (eval; same first windows)"]):
        for run in summary["runs"]:
            ax.plot(range(4), [row[metric] for row in run["history"]], "o-", label=f"Seed {run['seed']}")
        ax.plot(range(4), [row[metric]["mean"] for row in summary["epoch_statistics"]], "k--", linewidth=1.3, label="Mean of all 3 seeds")
        ax.set(title=title, xlabel="Epoch (0 = pretrained)", xticks=range(4), ylim=(0, None))
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Mean cross-entropy loss (lower is better)")
    axes[1].legend()
    fig.suptitle("AASIST Frozen BN pilot: same split, seeds 42 / 43 / 44")
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
