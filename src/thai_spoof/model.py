from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import torch

from .audio import load_audio, repeat_or_trim


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Prediction:
    path: Path
    prediction: str
    spoof_probability: float
    bonafide_probability: float
    bonafide_score: float
    device: str


class AASISTDetector:
    """Small inference wrapper around the official pretrained AASIST model."""

    def __init__(
        self,
        project_config: str | Path | None = None,
        device: str = "auto",
    ) -> None:
        config_path = Path(project_config or PROJECT_ROOT / "configs/project.json")
        if not config_path.is_absolute():
            config_path = PROJECT_ROOT / config_path
        with config_path.open("r", encoding="utf-8") as handle:
            project_config_data = json.load(handle)

        self.sample_rate = int(project_config_data["sample_rate"])
        self.num_samples = int(project_config_data["num_samples"])
        self.device = self._resolve_device(device)

        upstream_config_path = PROJECT_ROOT / project_config_data["aasist_config"]
        checkpoint_path = PROJECT_ROOT / project_config_data["aasist_checkpoint"]
        if not upstream_config_path.exists():
            raise FileNotFoundError(f"AASIST config not found: {upstream_config_path}")
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"AASIST checkpoint not found: {checkpoint_path}")

        with upstream_config_path.open("r", encoding="utf-8") as handle:
            upstream_config = json.load(handle)

        upstream_root = PROJECT_ROOT / "external/aasist"
        sys.path.insert(0, str(upstream_root))
        try:
            from models.AASIST import Model
        finally:
            sys.path.pop(0)

        self.model = Model(upstream_config["model_config"]).to(self.device)
        state_dict = torch.load(checkpoint_path, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state_dict)
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

    def predict(self, audio_path: str | Path) -> Prediction:
        path = Path(audio_path)
        waveform = load_audio(path, self.sample_rate)
        waveform = repeat_or_trim(waveform, self.num_samples)
        batch = torch.from_numpy(waveform).unsqueeze(0).to(self.device)

        with torch.inference_mode():
            _, logits = self.model(batch)
            probabilities = torch.softmax(logits, dim=1)[0]

        spoof_probability = float(probabilities[0].cpu())
        bonafide_probability = float(probabilities[1].cpu())
        prediction = "bonafide" if bonafide_probability >= spoof_probability else "spoof"
        return Prediction(
            path=path,
            prediction=prediction,
            spoof_probability=spoof_probability,
            bonafide_probability=bonafide_probability,
            bonafide_score=float(logits[0, 1].cpu()),
            device=str(self.device),
        )

