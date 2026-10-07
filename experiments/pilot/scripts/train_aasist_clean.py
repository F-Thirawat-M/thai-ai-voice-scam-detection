"""One-epoch Clean feasibility smoke; no Test, EER claim, best selection or resume.

Run with the main .venv, not .venv-wayu. Outputs are local and ignored by Git.
"""

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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import soundfile as sf
import torch
from torch.utils.data import DataLoader

from thai_spoof.aasist.detector import AASISTDetector
from thai_spoof.pilot.pilot_data import (
    LABEL_TO_INT, CleanPilotDataset, check_split_disjoint, file_sha256, load_pilot_split,
)
from thai_spoof.cvtts.provenance import verify_preparation_code


def evaluate(model, loader, device):
    model.eval()
    loss_sum = 0.0
    scores = []
    with torch.inference_mode():
        for x, y, indices in loader:
            _, logits = model(x.to(device))
            if logits.shape != (len(y), 2) or not torch.isfinite(logits).all():
                raise RuntimeError("invalid Dev logits")
            loss = torch.nn.functional.cross_entropy(logits, y.to(device), reduction="sum")
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite Dev loss")
            loss_sum += loss.item()
            for index, label, pair in zip(indices.tolist(), y.tolist(), logits.cpu().tolist()):
                scores.append({"index": index, "label_index": label, "spoof_logit": pair[0],
                               "bonafide_logit": pair[1], "bonafide_margin": pair[1] - pair[0]})
    return loss_sum / len(scores), scores


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="new output directory name; never overwrite an existing run")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--max-batches", type=int, default=0, help="0 = all 80 Train microbatches; 2 = separate short preflight")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.run_id):
        parser.error("run-id must be 1-80 letters, numbers, hyphens or underscores")
    if args.max_batches not in {0, 2}:
        parser.error("max-batches must be 0 (full epoch) or 2 (preflight)")
    if sys.prefix != str(ROOT / ".venv"):
        parser.error("use the project's main .venv Python, not .venv-wayu")
    output = ROOT / "results/pilot/aasist_clean_smoke" / args.run_id
    if output.exists():
        raise FileExistsError(f"run exists; use a NEW --run-id, do not delete or overwrite: {output}")

    report_path = ROOT / "data/processed/cvtts/pilot_v1/qc/canonical_audio/wayu_pilot_clean16k_v1.json"
    canonical = json.loads(report_path.read_text(encoding="utf-8"))
    if canonical["audio_policy"] != "mono16k_float_fullclip_v1":
        raise ValueError("unexpected audio policy")
    preparation_check = {name: verify_preparation_code(ROOT / name, digest)
                         for name, digest in canonical["preparation_code_sha256"].items()}
    train_rows, train_waves = load_pilot_split(ROOT, "train", canonical["manifest_sha256"]["wayu_pilot_train_clean16k.csv"])
    dev_rows, dev_waves = load_pilot_split(ROOT, "dev", canonical["manifest_sha256"]["wayu_pilot_dev_clean16k.csv"])
    check_split_disjoint(train_rows, dev_rows)
    print("Input audit passed: Train 160 / Dev 40; WAV mono 16 kHz; hashes checked; no Test.", flush=True)

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
    train = CleanPilotDataset(train_rows, train_waves, training=True, seed=seed)
    dev = CleanPilotDataset(dev_rows, dev_waves, training=False, seed=seed)
    generator = torch.Generator().manual_seed(seed + 1)  # shuffle RNG independent from crop RNG
    train_loader = DataLoader(train, batch_size=2, shuffle=True, generator=generator, num_workers=0)
    dev_loader = DataLoader(dev, batch_size=2, shuffle=False, num_workers=0)
    detector = AASISTDetector(device=args.device)
    model, device = detector.model, detector.device
    if detector.num_samples != 64600 or detector.sample_rate != 16000:
        raise ValueError("model wrapper config does not match the pilot window policy")
    config_path = ROOT / "external/aasist/config/AASIST.conf"
    upstream_config = json.loads(config_path.read_text(encoding="utf-8"))
    if upstream_config["model_config"]["nb_samp"] != 64600:
        raise ValueError("upstream model input length changed")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
        torch.cuda.synchronize(device)
    start = time.perf_counter()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5, weight_decay=1e-4)
    original_parameters = {name: p.detach().cpu().clone() for name, p in model.named_parameters()}
    batch_count = args.max_batches or len(train_loader)
    config = {
        "scope": "feasibility_smoke_only_not_main_research", "seed": seed, "epochs": 1,
        "max_batches": args.max_batches, "microbatch": 2, "gradient_accumulation": 8,
        "full_group_effective_batch": 16, "num_workers": 0,
        "optimizer": "AdamW", "learning_rate": 1e-5, "weight_decay": 1e-4,
        "lr_schedule": "constant", "loss": "unweighted_cross_entropy", "gradient_clip_norm": 1.0,
        "precision": "float32_no_AMP", "condition": "Clean_no_added_noise_or_telephone",
        "sample_rate": 16000, "num_samples": 64600,
        "train_crop": "random_inclusive_once_per_clip_for_one_epoch", "dev_crop": "first",
        "short_audio": "repeat", "amplitude_policy": "preserve_canonical_no_normalization",
        "frequency_mask_augmentation": False, "label_mapping": LABEL_TO_INT,
        "score_type": "bonafide_margin_v1", "checkpoint_selection": "last_only_no_best_selection",
        "resume_supported": False, "final_test_accessed": False, "generator_count": 1,
        "preflight_subset_only": bool(args.max_batches),
    }
    code_files = ["experiments/pilot/scripts/train_aasist_clean.py", "src/thai_spoof/pilot/pilot_data.py",
                  "src/thai_spoof/cvtts/windows.py", "src/thai_spoof/cvtts/provenance.py", "src/thai_spoof/aasist/detector.py",
                  "src/thai_spoof/aasist/config.json", "external/aasist/models/AASIST.py",
                  "external/aasist/data_utils.py"]
    run = {
        "run_id": args.run_id, "status": "running", "started_utc": datetime.now(timezone.utc).isoformat(),
        "config": config, "canonical_report_sha256": file_sha256(report_path),
        "preparation_code_verification": preparation_check,
        "manifest_sha256": canonical["manifest_sha256"],
        "initial_checkpoint_sha256": file_sha256(ROOT / "checkpoints/aasist/AASIST.pth"),
        "upstream_config_sha256": file_sha256(config_path),
        "code_sha256": {p: file_sha256(ROOT / p) for p in code_files},
        "environment": {"python": sys.version, "torch": torch.__version__, "numpy": np.__version__,
                        "soundfile": sf.__version__, "device": str(device),
                        "gpu": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
                        "cudnn_deterministic": True, "strict_bitwise_reproducibility_claimed": False},
        "parameters_total": sum(p.numel() for p in model.parameters()),
        "parameters_trainable": sum(p.numel() for p in model.parameters() if p.requires_grad),
        "input_counts": {"train": 160, "dev": 40},
    }
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "run.json", run)
    try:
        before_loss, before_scores = evaluate(model, dev_loader, device)
        print(f"Pretrained Dev loss: {before_loss:.6f} (diagnostic only, not Test accuracy)", flush=True)
        model.train()
        optimizer.zero_grad(set_to_none=True)
        microbatches = []
        updates = []
        exposures = []
        samples_seen = 0
        for number, (x, y, indices) in enumerate(train_loader, start=1):
            if number > batch_count:
                break
            group_start = ((number - 1) // 8) * 8
            group_size = min(8, batch_count - group_start)
            _, logits = model(x.to(device))  # deliberately NOT detector.predict()/inference_mode
            if logits.shape != (len(y), 2) or not torch.isfinite(logits).all():
                raise RuntimeError("invalid Train logits")
            loss = torch.nn.functional.cross_entropy(logits, y.to(device))
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite Train loss")
            (loss / group_size).backward()
            samples_seen += len(y)
            microbatches.append({"microbatch": number, "loss": loss.item()})
            for index in indices.tolist():
                row = train.rows[index]
                exposures.append({"sample_id": row["sample_id"], "label": row["label"], "crop_start": train.starts[index]})
            if number % 8 == 0 or number == batch_count:
                norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
                if norm.item() <= 0:
                    raise RuntimeError("zero gradients; no learning")
                optimizer.step()
                if any(not torch.isfinite(p).all() for p in model.parameters()):
                    raise RuntimeError("nonfinite parameters after update")
                optimizer.zero_grad(set_to_none=True)
                record = {"update": len(updates) + 1, "microbatch": number, "samples_seen": samples_seen,
                          "gradient_norm_before_clipping": norm.item(), "learning_rate": optimizer.param_groups[0]["lr"]}
                updates.append(record)
                print(f"Update {record['update']}: {number}/{batch_count} microbatches, loss={loss.item():.6f}, grad_norm={norm.item():.4f}", flush=True)
        changed = sum(not torch.equal(p.detach().cpu(), original_parameters[name]) for name, p in model.named_parameters())
        if not changed:
            raise RuntimeError("no model parameters changed")
        after_loss, after_scores = evaluate(model, dev_loader, device)
        saved_model = {name: value.detach().cpu().clone() for name, value in model.state_dict().items()}
        torch.save({"model": saved_model, "optimizer": optimizer.state_dict(), "config": config,
                    "optimizer_updates": len(updates), "torch_rng_state": torch.get_rng_state(),
                    "cuda_rng_states": torch.cuda.get_rng_state_all() if device.type == "cuda" else [],
                    "shuffle_generator_state": generator.get_state()}, output / "last.pt")
        reloaded = torch.load(output / "last.pt", map_location=device, weights_only=True)
        # Fresh instance; loading back into the same model could hide an incomplete state_dict.
        fresh_model = type(model)(upstream_config["model_config"]).to(device)
        fresh_model.load_state_dict(reloaded["model"], strict=True)
        reloaded_loss, reloaded_scores = evaluate(fresh_model, dev_loader, device)
        a = np.array([[s["spoof_logit"], s["bonafide_logit"]] for s in after_scores])
        b = np.array([[s["spoof_logit"], s["bonafide_logit"]] for s in reloaded_scores])
        np.testing.assert_allclose(a, b, rtol=1e-5, atol=1e-5)
        if device.type == "cuda":
            torch.cuda.synchronize(device)
        peak = torch.cuda.max_memory_allocated(device) if device.type == "cuda" else None
        run.update({"status": "completed", "optimizer_updates": len(updates), "microbatches": len(microbatches),
                    "samples_seen": samples_seen, "parameter_tensors_changed": changed,
                    "pretrained_dev_loss": before_loss, "trained_dev_loss": after_loss,
                    "reload_dev_loss": reloaded_loss, "reload_max_abs_logit_error": float(np.max(np.abs(a - b))),
                    "reload_tolerance": {"rtol": 1e-5, "atol": 1e-5},
                    "train_mean_loss": float(np.mean([r["loss"] for r in microbatches])),
                    "elapsed_seconds_including_dev_and_reload": time.perf_counter() - start,
                    "peak_cuda_allocated_bytes": peak,
                    "peak_cuda_reserved_bytes": torch.cuda.max_memory_reserved(device) if device.type == "cuda" else None,
                    "checkpoint_sha256": file_sha256(output / "last.pt"),
                    "exposures": {label: sum(r["label"] == label for r in exposures) for label in LABEL_TO_INT},
                    "not_evidence_of_generalization_or_fair_clean_mixed_comparison": True})
        with (output / "dev_scores.csv").open("x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["sample_id", "label", "stage", "spoof_logit", "bonafide_logit", "bonafide_margin"])
            writer.writeheader()
            for stage, scores in [("pretrained", before_scores), ("after_smoke", after_scores)]:
                for score in scores:
                    row = dev.rows[score["index"]]
                    writer.writerow({"sample_id": row["sample_id"], "label": row["label"], "stage": stage,
                                     **{key: score[key] for key in ["spoof_logit", "bonafide_logit", "bonafide_margin"]}})
        write_json(output / "training_log.json", {"microbatches": microbatches, "updates": updates, "sample_order_and_crops": exposures})
        run["dev_scores_sha256"] = file_sha256(output / "dev_scores.csv")
        run["training_log_sha256"] = file_sha256(output / "training_log.json")
        write_json(output / "run.json", run)
        print(f"Completed: {samples_seen} Train clips, {len(updates)} updates; {changed} parameter tensors changed; reload verified.", flush=True)
        print(f"Outputs: {output}\nSmoke only. No Test/EER; no claim of detector accuracy.", flush=True)
    except BaseException as error:
        run.update({"status": "failed", "error": f"{type(error).__name__}: {error}"})
        write_json(output / "run.json", run)
        raise


if __name__ == "__main__":
    main()
