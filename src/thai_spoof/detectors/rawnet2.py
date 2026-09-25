"""Inference adapter for the ASVspoof RawNet2 baseline."""

from __future__ import annotations

import copy
from pathlib import Path

import soundfile as sf
import torch
import torchaudio.functional as audio_f
import yaml

from .base import Prediction
from .rawnet2_arch import RawNet


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_RATE = 16_000
NUM_SAMPLES = 64_600


class RawNet2Detector:
    """Score the first 4.04 seconds, or average all segments when requested."""

    def __init__(
        self,
        config_path: str | Path | None = None,
        checkpoint_path: str | Path | None = None,
        device: str = "auto",
        all_chunks: bool = False,
    ) -> None:
        config = Path(config_path or PROJECT_ROOT / "configs/rawnet2.yaml")
        checkpoint = Path(
            checkpoint_path
            or PROJECT_ROOT / "checkpoints/rawnet2/pre_trained_DF_RawNet2.pth"
        )
        if not config.is_absolute():
            config = PROJECT_ROOT / config
        if not checkpoint.is_absolute():
            checkpoint = PROJECT_ROOT / checkpoint
        if not config.is_file():
            raise FileNotFoundError(f"RawNet2 config not found: {config}")
        if not checkpoint.is_file():
            raise FileNotFoundError(
                f"RawNet2 checkpoint not found: {checkpoint}. "
                "Run python scripts/setup_rawnet2_checkpoint.py first."
            )

        self.device = self._resolve_device(device)
        self.all_chunks = all_chunks
        with config.open(encoding="utf-8") as handle:
            model_config = yaml.safe_load(handle)
        self.model = RawNet(copy.deepcopy(model_config["model"]), str(self.device)).to(
            self.device
        )
        weights = torch.load(checkpoint, map_location=self.device, weights_only=True)
        if isinstance(weights, dict) and "state_dict" in weights:
            weights = weights["state_dict"]
        if not isinstance(weights, dict):
            raise TypeError("RawNet2 checkpoint does not contain a state_dict")
        weights = {key.removeprefix("module."): value for key, value in weights.items()}
        self.model.load_state_dict(weights, strict=True)
        self.model.eval()

    @staticmethod
    def _resolve_device(requested: str) -> torch.device:
        if requested == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if requested == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested, but PyTorch cannot access the GPU")
        if requested not in {"cpu", "cuda"}:
            raise ValueError("device must be one of: auto, cpu, cuda")
        return torch.device(requested)

    @staticmethod
    def _load_audio(path: Path) -> torch.Tensor:
        audio, sample_rate = sf.read(path, dtype="float32", always_2d=True)
        if audio.shape[0] == 0:
            raise ValueError(f"Audio file is empty: {path}")
        waveform = torch.from_numpy(audio).mean(dim=1)
        if not torch.isfinite(waveform).all():
            raise ValueError(f"Audio contains NaN or infinite samples: {path}")
        if sample_rate != SAMPLE_RATE:
            waveform = audio_f.resample(waveform, sample_rate, SAMPLE_RATE)
        if waveform.abs().max().item() == 0:
            raise ValueError(f"Audio file contains only silence: {path}")
        return waveform

    @staticmethod
    def _repeat_pad(waveform: torch.Tensor) -> torch.Tensor:
        if waveform.numel() >= NUM_SAMPLES:
            return waveform[:NUM_SAMPLES]
        repeats = (NUM_SAMPLES + waveform.numel() - 1) // waveform.numel()
        return waveform.repeat(repeats)[:NUM_SAMPLES]

    def predict(self, audio_path: str | Path) -> Prediction:
        path = Path(audio_path)
        waveform = self._load_audio(path)
        if self.all_chunks:
            segments = torch.stack(
                [
                    self._repeat_pad(waveform[start : start + NUM_SAMPLES])
                    for start in range(0, waveform.numel(), NUM_SAMPLES)
                ]
            )
        else:
            segments = self._repeat_pad(waveform).unsqueeze(0)

        with torch.inference_mode():
            probabilities = self.model(segments.to(self.device)).exp().mean(dim=0).cpu()
        spoof_probability = float(probabilities[0])
        bonafide_probability = float(probabilities[1])
        return Prediction(
            path=path,
            prediction="bonafide" if bonafide_probability >= 0.5 else "spoof",
            spoof_probability=spoof_probability,
            bonafide_probability=bonafide_probability,
            bonafide_score=bonafide_probability,
            device=str(self.device),
            model="rawnet2",
            score_type="softmax_probability",
            segments=int(segments.shape[0]),
        )
