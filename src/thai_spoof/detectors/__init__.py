"""Detector selection for the shared CLI and evaluation pipeline."""

from __future__ import annotations

from .aasist import AASISTDetector
from .base import Detector, Prediction
from .rawnet2 import RawNet2Detector


MODEL_NAMES = ("aasist", "rawnet2")


def create_detector(
    model_name: str, device: str = "auto", all_chunks: bool = False
) -> Detector:
    if model_name == "aasist":
        if all_chunks:
            raise ValueError("--all-chunks is currently supported only for RawNet2")
        return AASISTDetector(device=device)
    if model_name == "rawnet2":
        return RawNet2Detector(device=device, all_chunks=all_chunks)
    raise ValueError(f"unknown model: {model_name}; available: {', '.join(MODEL_NAMES)}")


__all__ = [
    "AASISTDetector",
    "RawNet2Detector",
    "Detector",
    "MODEL_NAMES",
    "Prediction",
    "create_detector",
]
