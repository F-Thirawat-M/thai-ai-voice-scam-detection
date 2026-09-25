from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .metrics import calculate_metrics
from .detectors import MODEL_NAMES, create_detector


def infer_command(args: argparse.Namespace) -> int:
    detector = create_detector(args.model, device=args.device, all_chunks=args.all_chunks)
    result = detector.predict(args.audio)
    print(f"file: {result.path}")
    print(f"device: {result.device}")
    print(f"model: {result.model}")
    print(f"segments: {result.segments}")
    print(f"prediction: {result.prediction}")
    print(f"bonafide_probability: {result.bonafide_probability:.6f}")
    print(f"spoof_probability: {result.spoof_probability:.6f}")
    print(f"bonafide_score: {result.bonafide_score:.6f}")
    print(f"score_type: {result.score_type}")
    print("warning: this pretrained score is not calibrated for Thai speech")
    return 0


def evaluate_command(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).resolve()
    output_path = Path(args.output).resolve()
    detector = create_detector(args.model, device=args.device, all_chunks=args.all_chunks)
    rows: list[dict[str, str]] = []

    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "path" not in reader.fieldnames:
            raise ValueError("manifest must contain a 'path' column")
        for row in reader:
            audio_path = Path(row["path"])
            if not audio_path.is_absolute():
                audio_path = Path.cwd() / audio_path
            result = detector.predict(audio_path)
            scored = dict(row)
            scored.update(
                {
                    "prediction": result.prediction,
                    "bonafide_probability": f"{result.bonafide_probability:.8f}",
                    "spoof_probability": f"{result.spoof_probability:.8f}",
                    "bonafide_score": f"{result.bonafide_score:.8f}",
                    "model": result.model,
                    "score_type": result.score_type,
                    "segments": str(result.segments),
                }
            )
            rows.append(scored)
            print(f"{row['path']}: {result.prediction}")

    if not rows:
        raise ValueError("manifest has no data rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"scores: {output_path}")

    labels = [row.get("label", "").strip().lower() for row in rows]
    if all(labels):
        metrics = calculate_metrics(
            labels,
            [float(row["bonafide_score"]) for row in rows],
        )
        metrics["model"] = args.model
        metrics["score_type"] = rows[0]["score_type"]
        metrics_path = output_path.with_suffix(".metrics.json")
        metrics_path.write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        print(f"metrics: {metrics_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Thai speech spoofing research utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    infer = subparsers.add_parser("infer", help="score one WAV or FLAC file")
    infer.add_argument("--audio", required=True, help="path to a WAV or FLAC file")
    infer.add_argument("--model", choices=MODEL_NAMES, default="aasist")
    infer.add_argument("--all-chunks", action="store_true", help="average all 4.04-second chunks (RawNet2 only)")
    infer.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    infer.set_defaults(func=infer_command)

    evaluate = subparsers.add_parser("evaluate", help="score files listed in a CSV")
    evaluate.add_argument("--manifest", required=True, help="CSV containing path and label")
    evaluate.add_argument("--output", required=True, help="output score CSV")
    evaluate.add_argument("--model", choices=MODEL_NAMES, default="aasist")
    evaluate.add_argument("--all-chunks", action="store_true", help="average all 4.04-second chunks (RawNet2 only)")
    evaluate.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    evaluate.set_defaults(func=evaluate_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
