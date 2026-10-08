"""Reuse seed 42, run only seeds 43/44 for exactly three epochs, report all three."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "src"))

from thai_spoof.pilot.pilot_data import file_sha256
from thai_spoof.pilot.seed_stability import validate_run, summarize_runs, plot_seed_curves


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="new suite name, 1-60 safe characters")
    parser.add_argument("--reference-run", default="frozen3_20261008_v1", help="existing seed-42 run name in frozen_bn_curve")
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args = parser.parse_args()
    for name in [args.run_id, args.reference_run]:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,59}", name):
            parser.error("names must be 1-60 letters/numbers/hyphens/underscores")
    if Path(sys.prefix).resolve() != (ROOT / ".venv").resolve():
        parser.error("use project's main .venv Python")
    output = ROOT / "results/pilot/aasist_seed_stability" / args.run_id
    base = ROOT / "results/pilot/aasist_frozen_bn_curve"
    reference = base / args.reference_run
    arms = [base / f"{args.run_id}_seed{seed}" for seed in [43, 44]]
    if any(path.exists() for path in [output, *arms]):
        raise FileExistsError("existing suite/seed run; choose NEW run-id; never overwrite")
    # Fail before training if the historical run is incomplete, tampered or incompatible.
    validate_run(reference, ROOT, 42)
    state = {"status": "running", "run_id": args.run_id, "started_utc": datetime.now(timezone.utc).isoformat(),
             "seeds": [42, 43, 44], "new_seeds_to_train": [43, 44], "reference_run": args.reference_run,
             "reference_run_json_sha256": file_sha256(reference / "run.json"), "driver_sha256": file_sha256(Path(__file__)),
             "summary_helper_sha256": file_sha256(ROOT / "src/thai_spoof/pilot/seed_stability.py"), "final_test_accessed": False}
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / "run.json", state)
    try:
        for seed, path in zip([43, 44], arms):
            print(f"\nSeed {seed}: fresh pretrained; 3 epochs; Train 160 / Dev 40.", flush=True)
            subprocess.run([sys.executable, "-u", str(ROOT / "experiments/pilot/scripts/aasist/train_aasist_frozen_bn.py"),
                            "--run-id", path.name, "--seed", str(seed), "--device", args.device], cwd=ROOT, check=True)
        if file_sha256(reference / "run.json") != state["reference_run_json_sha256"]:
            raise ValueError("reference run changed during suite")
        summary = summarize_runs([reference, *arms], ROOT)
        write_json(output / "summary.json", summary)
        plot_seed_curves(summary, output / "seed_curves.png")
        state.update({"status": "completed", "controls_passed": True, "summary_sha256": file_sha256(output / "summary.json"),
                      "plot_sha256": file_sha256(output / "seed_curves.png")})
        write_json(output / "run.json", state)
        values = summary["epoch_statistics"][3]["dev_loss"]
        print(f"\nEpoch-3 Dev CE across ALL seeds: mean={values['mean']:.6f}, sample SD={values['sample_std_ddof1']:.6f}", flush=True)
        print(f"Verified summary: {output}. No best seed selection; no Test/EER.", flush=True)
    except BaseException as error:
        state.update({"status": "failed", "error": f"{type(error).__name__}: {error}"})
        write_json(output / "run.json", state)
        raise


if __name__ == "__main__":
    main()
