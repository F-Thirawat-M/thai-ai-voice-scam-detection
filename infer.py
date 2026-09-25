#!/usr/bin/env python3
"""Run the official ASVspoof 2021 RawNet2 baseline on ordinary audio files."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import soundfile as sf
import torch
import torchaudio.functional as AF
import yaml

from model import RawNet


ROOT = Path(__file__).resolve().parent
DEFAULT_CHECKPOINT = ROOT / "checkpoints" / "pre_trained_DF_RawNet2.pth"
DEFAULT_CONFIG = ROOT / "model_config_RawNet.yaml"
TARGET_SAMPLE_RATE = 16_000
TARGET_SAMPLES = 64_600


def choose_device(requested: str) -> torch.device:
    if requested != "auto":
        return torch.device(requested)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_audio(path: Path) -> torch.Tensor:
    audio, sample_rate = sf.read(path, dtype="float32", always_2d=True)
    if audio.shape[0] == 0:
        raise ValueError("audio file is empty")
    waveform = torch.from_numpy(audio).mean(dim=1)
    if sample_rate != TARGET_SAMPLE_RATE:
        waveform = AF.resample(waveform, sample_rate, TARGET_SAMPLE_RATE)
    peak = waveform.abs().max().item()
    if peak == 0:
        raise ValueError("audio file contains only silence")
    return waveform


def repeat_pad(waveform: torch.Tensor, size: int = TARGET_SAMPLES) -> torch.Tensor:
    if waveform.numel() >= size:
        return waveform[:size]
    repeats = (size + waveform.numel() - 1) // waveform.numel()
    return waveform.repeat(repeats)[:size]


def make_segments(waveform: torch.Tensor, all_chunks: bool) -> torch.Tensor:
    if not all_chunks:
        return repeat_pad(waveform).unsqueeze(0)
    segments = []
    for start in range(0, waveform.numel(), TARGET_SAMPLES):
        segments.append(repeat_pad(waveform[start : start + TARGET_SAMPLES]))
    return torch.stack(segments)


def load_model(config_path: Path, checkpoint_path: Path, device: torch.device) -> RawNet:
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    model = RawNet(copy.deepcopy(config["model"]), str(device)).to(device)
    try:
        checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    except TypeError:
        checkpoint = torch.load(checkpoint_path, map_location=device)
    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        checkpoint = checkpoint["state_dict"]
    if not isinstance(checkpoint, dict):
        raise TypeError("checkpoint does not contain a PyTorch state_dict")
    checkpoint = {key.removeprefix("module."): value for key, value in checkpoint.items()}
    model.load_state_dict(checkpoint, strict=True)
    model.eval()
    return model


def score_file(
    path: Path,
    model: RawNet,
    device: torch.device,
    all_chunks: bool,
    threshold: float,
) -> dict[str, object]:
    waveform = load_audio(path)
    segments = make_segments(waveform, all_chunks).to(device)
    with torch.inference_mode():
        log_probabilities = model(segments)
        probabilities = log_probabilities.exp().mean(dim=0).cpu()
    spoof_probability = float(probabilities[0])
    bonafide_probability = float(probabilities[1])
    return {
        "file": str(path.resolve()),
        "sample_rate": TARGET_SAMPLE_RATE,
        "segments": int(segments.shape[0]),
        "spoof_score": spoof_probability,
        "bonafide_score": bonafide_probability,
        "prediction": "bonafide" if bonafide_probability >= threshold else "spoof",
        "threshold": threshold,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Classify audio as bonafide or spoof with the pretrained RawNet2 baseline."
    )
    parser.add_argument("audio", nargs="+", type=Path, help="WAV or FLAC file(s)")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--device", choices=("auto", "cpu", "mps", "cuda"), default="auto")
    parser.add_argument(
        "--all-chunks",
        action="store_true",
        help="score every 4.04-second chunk and average; default matches the baseline's first-chunk behavior",
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0.0 <= args.threshold <= 1.0:
        raise SystemExit("--threshold must be between 0 and 1")
    if not args.checkpoint.is_file():
        raise SystemExit(
            f"Checkpoint not found: {args.checkpoint}\n"
            "Run ./setup_checkpoint.sh first."
        )
    missing = [str(path) for path in args.audio if not path.is_file()]
    if missing:
        raise SystemExit("Audio file(s) not found: " + ", ".join(missing))

    device = choose_device(args.device)
    model = load_model(args.config, args.checkpoint, device)
    results = [
        score_file(path, model, device, args.all_chunks, args.threshold)
        for path in args.audio
    ]
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    print(f"Device: {device}")
    for result in results:
        print(
            f"{result['file']}\n"
            f"  prediction={result['prediction']}  "
            f"bonafide_score={result['bonafide_score']:.6f}  "
            f"spoof_score={result['spoof_score']:.6f}  "
            f"segments={result['segments']}"
        )


if __name__ == "__main__":
    main()
