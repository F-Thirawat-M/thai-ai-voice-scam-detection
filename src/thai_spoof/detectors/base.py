"""Shared result and interface for speech spoofing detectors."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Prediction:
    """A detector result; higher bonafide_score means stronger bona fide evidence.

    The score scale depends on the model and is not calibrated across models.
    """

    path: Path
    prediction: str
    spoof_probability: float
    bonafide_probability: float
    bonafide_score: float
    device: str
    model: str
    score_type: str
    segments: int


class Detector(Protocol):
    def predict(self, audio_path: str | Path) -> Prediction: ...
