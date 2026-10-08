"""Exactly three fresh Clean epochs with Frozen BN; Train/Dev only, no resume/Test."""

from __future__ import annotations

import argparse
import csv
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
import soundfile as sf
import torch
from torch.utils.data import DataLoader

from thai_spoof.aasist.detector import AASISTDetector
from thai_spoof.cvtts.provenance import verify_preparation_code
from thai_spoof.pilot.batchnorm import snapshot_bn_buffers, summarize_bn_changes
from thai_spoof.pilot.learning_curve import evaluate_split, train_frozen_epoch, select_best_trained_epoch, plot_loss_curve
from thai_spoof.pilot.pilot_data import LABEL_TO_INT, CleanPilotDataset, load_pilot_split, check_split_disjoint, file_sha256


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def verify_reload(model, checkpoint, model_config, dev_loader, device, expected_scores) -> float:
    # Constructing a fresh model consumes random numbers. Verification must not
    # change the dropout trajectory of the original model in the next epoch.
    devices = [device.index if device.index is not None else torch.cuda.current_device()] if device.type == "cuda" else []
    with torch.random.fork_rng(devices=devices):
        fresh = type(model)(model_config).to(device)
        saved = torch.load(checkpoint, map_location=device, weights_only=True)
        fresh.load_state_dict(saved["model"], strict=True)
        _, actual_scores = evaluate_split(fresh, dev_loader, device)
        expected = np.array([[s["spoof_logit"], s["bonafide_logit"]] for s in expected_scores])
        actual = np.array([[s["spoof_logit"], s["bonafide_logit"]] for s in actual_scores])
        np.testing.assert_allclose(actual, expected, rtol=1e-5, atol=1e-5)
        return float(np.max(np.abs(actual - expected)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--seed", type=int, default=42, help="seed for fixed crop, shuffle and dropout (default: 42)")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.run_id):
        parser.error("use 1-80 letters/numbers/hyphens/underscores")
    if not 0 <= args.seed <= 2**32 - 2:
        parser.error("seed must be between 0 and 4294967294")
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        parser.error("use project's main .venv Python")
    output = ROOT / "results/pilot/aasist_frozen_bn_curve" / args.run_id
    if output.exists():
        raise FileExistsError("existing run; choose NEW run-id; never overwrite")

    report_path = ROOT / "data/processed/cvtts/pilot_v1/qc/canonical_audio/wayu_pilot_clean16k_v1.json"
    canonical = json.loads(report_path.read_text(encoding="utf-8"))
    if canonical["audio_policy"] != "mono16k_float_fullclip_v1":
        raise ValueError("unexpected canonical audio policy")
    preparation = {name: verify_preparation_code(ROOT / name, digest) for name, digest in canonical["preparation_code_sha256"].items()}
    rows, waves = load_pilot_split(ROOT, "train", canonical["manifest_sha256"]["wayu_pilot_train_clean16k.csv"])
    dev_rows, dev_waves = load_pilot_split(ROOT, "dev", canonical["manifest_sha256"]["wayu_pilot_dev_clean16k.csv"])
    check_split_disjoint(rows, dev_rows)
    print("Input audit passed: Train 160 / Dev 40; three epochs; no Test.", flush=True)

    seed = args.seed
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
    # Deliberately reuse the same seeded windows for all 3 epochs: epoch budget
    # is the only intended recipe extension from the Frozen-BN one-epoch arm.
    train = CleanPilotDataset(rows, waves, training=True, seed=seed)
    dev = CleanPilotDataset(dev_rows, dev_waves, training=False, seed=seed)
    generator = torch.Generator().manual_seed(seed + 1)
    train_loader = DataLoader(train, batch_size=2, shuffle=True, generator=generator, num_workers=0)
    train_eval_loader = DataLoader(train, batch_size=2, shuffle=False, num_workers=0)
    dev_loader = DataLoader(dev, batch_size=2, shuffle=False, num_workers=0)
    detector = AASISTDetector(device=args.device)
    model, device = detector.model, detector.device
    if detector.num_samples != 64600 or detector.sample_rate != 16000:
        raise ValueError("model input window mismatch")
    config_path = ROOT / "external/aasist/config/AASIST.conf"
    upstream = json.loads(config_path.read_text(encoding="utf-8"))
    if upstream["model_config"]["nb_samp"] != 64600:
        raise ValueError("upstream input mismatch")
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5, weight_decay=1e-4)
    original = {name: p.detach().cpu().clone() for name, p in model.named_parameters()}
    bn_original = snapshot_bn_buffers(model)
    config = {"scope": "bounded_three_epoch_Frozen_BN_pilot_not_main_research", "seed": seed, "epochs": 3,
              "microbatch": 2, "gradient_accumulation": 8, "effective_batch": 16,
              "optimizer": "AdamW", "learning_rate": 1e-5, "weight_decay": 1e-4,
              "lr_schedule": "constant", "gradient_clip_norm": 1.0, "loss": "unweighted_cross_entropy",
              "precision": "float32_no_AMP", "num_workers": 0, "condition": "Clean_no_added_noise_or_telephone",
              "sample_rate": 16000, "num_samples": 64600, "label_mapping": LABEL_TO_INT,
              "batchnorm_mode": "frozen", "bn_affine_parameters_trainable": True, "dropout_training_mode": "train",
              "train_crop": "seeded_random_once_per_clip_reused_all_3_epochs", "dev_crop": "first", "short_audio": "repeat",
              "amplitude_policy": "preserve_canonical_no_normalization", "frequency_mask_augmentation": False,
              "monitoring": "Train_and_Dev_in_eval_mode; extra_Train_monitoring_and_reload_preserve_RNG",
              "checkpoint_selection": "lowest_post_epoch_Dev_CE_among_epochs_1_to_3; earliest_tie; epoch0_reference_only",
              "early_stopping": False, "resume_supported": False, "final_test_accessed": False}
    code_paths = ["experiments/pilot/scripts/aasist/train_aasist_frozen_bn.py", "src/thai_spoof/pilot/learning_curve.py",
                  "src/thai_spoof/pilot/batchnorm.py", "src/thai_spoof/pilot/pilot_data.py", "src/thai_spoof/cvtts/windows.py",
                  "src/thai_spoof/cvtts/provenance.py", "src/thai_spoof/aasist/detector.py", "src/thai_spoof/aasist/config.json",
                  "external/aasist/models/AASIST.py", "external/aasist/data_utils.py"]
    run = {"status": "running", "run_id": args.run_id, "started_utc": datetime.now(timezone.utc).isoformat(), "config": config,
           "canonical_report_sha256": file_sha256(report_path), "manifest_sha256": canonical["manifest_sha256"],
           "preparation_code_verification": preparation, "initial_checkpoint_sha256": file_sha256(ROOT / "checkpoints/aasist/AASIST.pth"),
           "upstream_config_sha256": file_sha256(config_path), "code_sha256": {name: file_sha256(ROOT / name) for name in code_paths},
           "input_counts": {"train": 160, "dev": 40},
           "parameters_total": sum(p.numel() for p in model.parameters()),
           "parameters_trainable": sum(p.numel() for p in model.parameters() if p.requires_grad),
           "environment": {"python": sys.version, "torch": torch.__version__, "numpy": np.__version__, "soundfile": sf.__version__,
                           "device": str(device), "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
                           "cudnn_deterministic": True, "strict_bitwise_reproducibility_claimed": False}}
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "run.json", run)
    history, training_log = [], []
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
    start = time.perf_counter()
    try:
        train_loss, train_scores = evaluate_split(model, train_eval_loader, device)
        # Preserve the original one-epoch script's initial Dev iteration behavior.
        dev_loss, dev_scores = evaluate_split(model, dev_loader, device, preserve_rng=False)
        history.append({"epoch": 0, "train_evaluation_loss": train_loss, "dev_loss": dev_loss})
        print(f"Pretrained: Train(eval)={train_loss:.6f}, Dev={dev_loss:.6f}", flush=True)
        with (output / "scores.csv").open("x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["epoch", "split", "sample_id", "label", "spoof_logit", "bonafide_logit", "bonafide_margin"])
            writer.writeheader()
            def save_scores(epoch, split, scores, dataset):
                for score in scores:
                    row = dataset.rows[score["index"]]
                    writer.writerow({"epoch": epoch, "split": split, "sample_id": row["sample_id"], "label": row["label"],
                                     **{key: score[key] for key in ["spoof_logit", "bonafide_logit", "bonafide_margin"]}})
                handle.flush()
            save_scores(0, "train", train_scores, train)
            save_scores(0, "dev", dev_scores, dev)
            for epoch in range(1, 4):
                stats = train_frozen_epoch(model, train_loader, optimizer, device)
                indices = stats.pop("sample_indices")
                if stats["samples_seen"] != 160 or len(stats["updates"]) != 10 or len(stats["microbatches"]) != 80 or sorted(indices) != list(range(160)):
                    raise RuntimeError("incomplete/duplicate Train epoch")
                order = [{"sample_id": train.rows[i]["sample_id"], "label": train.rows[i]["label"], "crop_start": train.starts[i]} for i in indices]
                training_log.append({"epoch": epoch, **stats, "sample_order_and_crops": order})
                train_loss, train_scores = evaluate_split(model, train_eval_loader, device)
                dev_loss, dev_scores = evaluate_split(model, dev_loader, device)
                checkpoint = output / f"epoch_{epoch:03d}.pt"
                torch.save({"model": {name: value.detach().cpu().clone() for name, value in model.state_dict().items()},
                            "optimizer": optimizer.state_dict(), "config": config, "epoch": epoch, "optimizer_updates": epoch * 10}, checkpoint)
                reload_error = verify_reload(model, checkpoint, upstream["model_config"], dev_loader, device, dev_scores)
                history.append({"epoch": epoch, "train_evaluation_loss": train_loss, "dev_loss": dev_loss,
                                "train_optimization_mean_loss": stats["train_optimization_mean_loss"],
                                "checkpoint": checkpoint.name, "checkpoint_sha256": file_sha256(checkpoint),
                                "reload_max_abs_logit_error": reload_error})
                save_scores(epoch, "train", train_scores, train)
                save_scores(epoch, "dev", dev_scores, dev)
                write_json(output / "learning_curve.json", {"history": history, "metric": "mean_CE_eval_mode_fixed_windows"})
                write_json(output / "training_log.json", {"epochs": training_log})
                print(f"Epoch {epoch}/3: Train(eval)={train_loss:.6f}, Dev={dev_loss:.6f}, 10 updates, reload verified.", flush=True)
        audit = summarize_bn_changes(bn_original, snapshot_bn_buffers(model))
        if audit["changed_buffer_count"]:
            raise RuntimeError("Frozen BN buffers changed across epochs")
        changed = sum(not torch.equal(p.detach().cpu(), original[name]) for name, p in model.named_parameters())
        if not changed:
            raise RuntimeError("parameters did not learn")
        best_epoch = select_best_trained_epoch(history)
        best = history[best_epoch]
        write_json(output / "selection.json", {"rule": config["checkpoint_selection"], "best_epoch": best_epoch,
                  "checkpoint": best["checkpoint"], "checkpoint_sha256": best["checkpoint_sha256"], "dev_loss": best["dev_loss"],
                  "pretrained_dev_loss": history[0]["dev_loss"], "trained_best_beats_pretrained_CE": best["dev_loss"] < history[0]["dev_loss"],
                  "final_test_accessed": False})
        plot_loss_curve(history, output / "loss_curve.png")
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        run.update({"status": "completed", "epochs_completed": 3, "optimizer_updates": 30, "clip_exposures": 480,
                    "unique_Train_clips": 160, "history": history, "best_epoch": best_epoch, "best_checkpoint": best["checkpoint"],
                    "parameter_tensors_changed": changed, "batchnorm_audit": audit,
                    "elapsed_seconds_including_evaluation_reload_plot": time.perf_counter() - start,
                    "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None,
                    "peak_cuda_reserved_bytes": torch.cuda.max_memory_reserved(device) if device.type == "cuda" else None,
                    "artifact_sha256": {name: file_sha256(output / name) for name in ["scores.csv", "training_log.json", "learning_curve.json", "selection.json", "loss_curve.png"]},
                    "not_evidence_of_Test_accuracy_or_final_recipe": True})
        write_json(output / "run.json", run)
        print(f"Completed 3 epochs. Best trained epoch by Dev CE: {best_epoch}; Dev={best['dev_loss']:.6f}. No Test/EER.", flush=True)
        print(f"Outputs: {output}", flush=True)
    except BaseException as error:
        run.update({"status": "failed", "error": f"{type(error).__name__}: {error}", "history": history})
        write_json(output / "run.json", run)
        raise


if __name__ == "__main__":
    main()
