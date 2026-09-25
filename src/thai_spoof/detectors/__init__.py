"""Detector selection for the shared CLI and evaluation pipeline."""

from __future__ import annotations

from .aasist import AASISTDetector
from .base import Detector, Prediction


MODEL_NAMES = ("aasist",)


def create_detector(model_name: str, device: str = "auto") -> Detector:
    if model_name == "aasist":
        return AASISTDetector(device=device)
    raise ValueError(f"unknown model: {model_name}; available: {', '.join(MODEL_NAMES)}")


__all__ = ["AASISTDetector", "Detector", "MODEL_NAMES", "Prediction", "create_detector"]
