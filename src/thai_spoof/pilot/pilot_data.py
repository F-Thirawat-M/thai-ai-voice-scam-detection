"""Strict loader for the already audited Wayu clean pilot, not arbitrary datasets."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from torch.utils.data import Dataset

from ..cvtts.audio import CANONICAL_POLICY
from ..cvtts.windows import select_window


LABEL_TO_INT = {"spoof": 0, "bonafide": 1}  # upstream aasist/data_utils.py


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pilot_split(root: Path, split: str, expected_hash: str) -> tuple[list[dict], list[np.ndarray]]:
    if split not in {"train", "dev"}:
        raise ValueError("only Train/Dev are supported; there is no Test loader")
    base = root / "data/processed/cvtts/pilot_v1"
    manifest = base / "manifests" / f"wayu_pilot_{split}_clean16k.csv"
    if file_sha256(manifest) != expected_hash:
        raise ValueError(f"manifest hash mismatch: {manifest}")
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected = 160 if split == "train" else 40
    if len(rows) != expected or any(sum(r["label"] == label for r in rows) != expected // 2 for label in LABEL_TO_INT):
        raise ValueError("unexpected pilot label counts")
    for column in ["sample_id", "audio_file_sha256", "waveform_sha256"]:
        if len({r[column] for r in rows}) != expected:
            raise ValueError(f"duplicate {column}")
    for column in ["source_sample_id", "source_text_key"]:
        groups: dict[str, list[str]] = {}
        for row in rows:
            groups.setdefault(row[column], []).append(row["label"])
        if any(sorted(labels) != ["bonafide", "spoof"] for labels in groups.values()):
            raise ValueError(f"unpaired source: {column}")
    waves = []
    for row in rows:
        if row["split"] != split or row["audio_policy"] != CANONICAL_POLICY:
            raise ValueError("split or audio policy mismatch")
        path = (root / row["audio_path"]).resolve()
        if not path.is_relative_to((base / "canonical/clean16k" / split / row["label"]).resolve()):
            raise ValueError("audio path outside expected canonical split/class")
        if file_sha256(path) != row["audio_file_sha256"]:
            raise ValueError(f"audio hash mismatch: {path}")
        source_path = (root / row["source_audio_path"]).resolve()
        source_base = root / ("data/raw/common_voice" if row["label"] == "bonafide" else f"data/processed/cvtts/pilot_v1/native_tts/wayu/{split}")
        if not source_path.is_relative_to(source_base.resolve()) or file_sha256(source_path) != row["source_audio_file_sha256"]:
            raise ValueError("source path/hash mismatch")
        info = sf.info(path)
        x, sr = sf.read(path, dtype="float32")
        if sr != 16000 or info.channels != 1 or info.subtype != "FLOAT" or len(x) != int(row["frames"]):
            raise ValueError(f"canonical header mismatch: {path}")
        if not x.size or not np.isfinite(x).all() or np.max(np.abs(x)) <= 1e-8:
            raise ValueError(f"invalid audio: {path}")
        if hashlib.sha256(x.astype("<f4").tobytes()).hexdigest() != row["waveform_sha256"]:
            raise ValueError("waveform hash mismatch")
        waves.append(x)
    return rows, waves


def check_split_disjoint(train: list[dict], dev: list[dict]) -> None:
    for key in ["sample_id", "source_sample_id", "source_text_key", "audio_file_sha256", "waveform_sha256", "source_audio_file_sha256"]:
        if {r[key] for r in train} & {r[key] for r in dev}:
            raise ValueError(f"Train/Dev overlap: {key}")


class CleanPilotDataset(Dataset):
    """One fixed seeded random crop per Train clip for this one-epoch smoke only."""

    def __init__(self, rows: list[dict], waves: list[np.ndarray], *, training: bool, seed: int):
        if len(rows) != len(waves):
            raise ValueError("rows and waves must have equal lengths")
        rng = np.random.default_rng(seed) if training else None
        self.rows = rows
        self.windows = []
        self.starts = []
        for x in waves:
            window, start = select_window(x, rng=rng)
            self.windows.append(torch.from_numpy(window))
            self.starts.append(start)

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        return self.windows[index], LABEL_TO_INT[self.rows[index]["label"]], index
