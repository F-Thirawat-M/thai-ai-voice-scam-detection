"""Memorize two paired Train texts (4 clips). No Dev/Test is loaded or scored."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import torch

from thai_spoof.aasist.detector import AASISTDetector
from thai_spoof.pilot.overfit import evaluate_fixed, fit_fixed_batch, select_train_pairs
from thai_spoof.pilot.pilot_data import CleanPilotDataset, file_sha256, load_pilot_split
from thai_spoof.cvtts.provenance import verify_preparation_code


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"])
    parser.add_argument("--max-updates", type=int, default=100)
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.run_id):
        parser.error("invalid run-id; use 1-80 letters/numbers/hyphens/underscores")
    if not 20 <= args.max_updates <= 200:
        parser.error("max-updates must be 20-200; this is a bounded diagnostic")
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        parser.error("use the project's main .venv Python")
    output = ROOT / "results/pilot/aasist_overfit_check" / args.run_id
    if output.exists():
        raise FileExistsError(f"existing run; choose NEW run-id, never overwrite: {output}")
    report_path = ROOT / "data/processed/cvtts/pilot_v1/qc/canonical_audio/wayu_pilot_clean16k_v1.json"
    canonical = json.loads(report_path.read_text(encoding="utf-8"))
    if canonical["audio_policy"] != "mono16k_float_fullclip_v1":
        raise ValueError("unexpected canonical policy")
    preparation_check = {name: verify_preparation_code(ROOT / name, digest)
                         for name, digest in canonical["preparation_code_sha256"].items()}
    # Deliberately no Dev/Test loader: the only data read are Train and its source audio.
    rows, waves = load_pilot_split(ROOT, "train", canonical["manifest_sha256"]["wayu_pilot_train_clean16k.csv"])
    indices = select_train_pairs(rows, pairs=2, seed=42)
    selected_rows = [rows[i] for i in indices]
    selected_waves = [waves[i] for i in indices]
    dataset = CleanPilotDataset(selected_rows, selected_waves, training=True, seed=42)
    x = torch.stack(dataset.windows)
    y = torch.tensor([dataset[i][1] for i in range(len(dataset))], dtype=torch.long)
    seed = 42
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.set_num_threads(2)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    detector = AASISTDetector(device=args.device)
    model, device = detector.model, detector.device
    if detector.num_samples != 64600 or detector.sample_rate != 16000:
        raise ValueError("AASIST wrapper input mismatch")
    config_path = ROOT / "external/aasist/config/AASIST.conf"
    upstream = json.loads(config_path.read_text(encoding="utf-8"))
    if upstream["model_config"]["nb_samp"] != 64600:
        raise ValueError("upstream input mismatch")
    original = {name: p.detach().cpu().clone() for name, p in model.named_parameters()}
    buffers = {name: b.detach().cpu().clone() for name, b in model.named_buffers()}
    x, y = x.to(device), y.to(device)
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
    start = time.perf_counter()
    code = ["experiments/pilot/scripts/aasist/check_aasist_overfit.py", "src/thai_spoof/pilot/overfit.py",
            "src/thai_spoof/cvtts/windows.py", "src/thai_spoof/pilot/pilot_data.py", "src/thai_spoof/cvtts/provenance.py",
            "src/thai_spoof/aasist/detector.py", "src/thai_spoof/aasist/config.json",
            "external/aasist/models/AASIST.py", "external/aasist/data_utils.py"]
    run = {
        "status": "running", "run_id": args.run_id, "started_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "fixed_Train_subset_memorization_diagnostic_not_generalization",
        "config": {"subset": "2 paired Train texts: 2 bonafide + 2 Wayu", "seed": seed,
                   "microbatch": 2, "effective_batch": 4, "max_updates": args.max_updates,
                   "min_updates": 20, "check_every_updates": 5, "optimizer": "AdamW",
                   "lr": 1e-4, "weight_decay": 0, "gradient_clip_norm": 1.0,
                   "loss": "unweighted_cross_entropy", "precision": "float32_no_AMP",
                   "input_samples": 64600, "sample_rate": 16000,
                   "input_windows": "seeded random inclusive crop once then fixed; short repeat",
                   "amplitude": "preserve_canonical", "model_mode": "eval_WITH_autograd",
                   "dropout": "disabled", "BatchNorm_running_stats": "frozen",
                   "all_parameters_trainable": True, "augmentation": "none",
                   "pass_rule": "on SAME Train subset: argmax accuracy=1.0 AND CE<=0.1 after >=20 updates",
                   "label_mapping": {"spoof": 0, "bonafide": 1}, "resume_supported": False},
        "dev_loaded_or_scored": False, "test_loaded_or_scored": False,
        "initial_checkpoint_sha256": file_sha256(ROOT / "checkpoints/aasist/AASIST.pth"),
        "canonical_report_sha256": file_sha256(report_path),
        "preparation_code_verification": preparation_check,
        "train_manifest_sha256": canonical["manifest_sha256"]["wayu_pilot_train_clean16k.csv"],
        "upstream_config_sha256": file_sha256(config_path), "code_sha256": {p: file_sha256(ROOT / p) for p in code},
        "environment": {"python": sys.version, "torch": torch.__version__, "numpy": np.__version__,
                        "device": str(device), "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
                        "strict_bitwise_reproducibility_claimed": False},
        "selected": [{"sample_id": row["sample_id"], "label": row["label"], "source_sample_id": row["source_sample_id"],
                      "audio_path": row["audio_path"], "audio_file_sha256": row["audio_file_sha256"],
                      "crop_start": dataset.starts[i],
                      "window_sha256": hashlib.sha256(dataset.windows[i].numpy().astype("<f4").tobytes()).hexdigest()}
                     for i, row in enumerate(selected_rows)],
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "run.json", run)
    history = []
    def progress(row):
        history.append(row)
        write_json(output / "training_log.json", {"history": history})
        if "loss" in row:
            print(f"Update {row['update']}: SAME Train-subset loss={row['loss']:.6f}, accuracy={row['accuracy']:.0%}", flush=True)
    try:
        print("Audited Train only; selected fixed 4 clips (2 real / 2 Wayu). Starting from original pretrained.", flush=True)
        fit_history, optimizer, passed = fit_fixed_batch(model, x, y, max_updates=args.max_updates, callback=progress)
        assert len(history) == len(fit_history)
        final = evaluate_fixed(model, x, y)
        changed = sum(not torch.equal(p.detach().cpu(), original[name]) for name, p in model.named_parameters())
        buffers_unchanged = all(torch.equal(b.detach().cpu(), buffers[name]) for name, b in model.named_buffers())
        if not changed or not buffers_unchanged:
            raise RuntimeError("parameters did not change or frozen buffers changed")
        updates = history[-1]["update"]
        torch.save({"model": {k: v.detach().cpu().clone() for k, v in model.state_dict().items()},
                    "optimizer": optimizer.state_dict(), "config": run["config"], "updates": updates}, output / "last.pt")
        saved = torch.load(output / "last.pt", map_location=device, weights_only=True)
        fresh_model = type(model)(upstream["model_config"]).to(device)
        fresh_model.load_state_dict(saved["model"], strict=True)
        restored = evaluate_fixed(fresh_model, x, y)
        a, b = np.array(final["logits"]), np.array(restored["logits"])
        np.testing.assert_allclose(a, b, rtol=1e-5, atol=1e-5)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        run.update({"status": "completed", "diagnostic_passed": passed,
                    "updates": updates, "microbatches": updates * 2, "clip_exposures": updates * 4,
                    "before_subset_loss": history[0]["loss"], "before_subset_accuracy": history[0]["accuracy"],
                    "after_subset_loss": final["loss"], "after_subset_accuracy": final["accuracy"],
                    "parameter_tensors_changed": changed, "model_buffers_unchanged": buffers_unchanged,
                    "reload_max_abs_logit_error": float(np.abs(a - b).max()),
                    "reload_tolerance": {"rtol": 1e-5, "atol": 1e-5},
                    "elapsed_seconds_including_subset_eval_and_reload": time.perf_counter() - start,
                    "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None,
                    "peak_cuda_reserved_bytes": torch.cuda.max_memory_reserved(device) if device.type == "cuda" else None,
                    "checkpoint_sha256": file_sha256(output / "last.pt"),
                    "not_a_main_recipe_or_evidence_of_unseen_audio_accuracy": True,
                    "did_not_identify_the_cause_of_previous_Dev_loss_increase": True})
        with (output / "subset_scores.csv").open("x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "label", "stage", "spoof_logit", "bonafide_logit", "prediction"])
            writer.writeheader()
            for stage, result in [("pretrained", history[0]), ("after_overfit", final)]:
                for i, row in enumerate(selected_rows):
                    writer.writerow({"sample_id": row["sample_id"], "label": row["label"], "stage": stage,
                                     "spoof_logit": result["logits"][i][0], "bonafide_logit": result["logits"][i][1],
                                     "prediction": "bonafide" if result["predictions"][i] == 1 else "spoof"})
        run["subset_scores_sha256"] = file_sha256(output / "subset_scores.csv")
        run["training_log_sha256"] = file_sha256(output / "training_log.json")
        write_json(output / "run.json", run)
        print(f"Completed; memorization diagnostic passed={passed}. {updates} updates. No Dev/Test used.\n{output}", flush=True)
    except BaseException as error:
        run.update({"status": "failed", "error": f"{type(error).__name__}: {error}"})
        write_json(output / "run.json", run)
        raise


if __name__ == "__main__":
    main()
