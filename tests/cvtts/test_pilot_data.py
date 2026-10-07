import csv
import hashlib

import numpy as np
import pytest

from thai_spoof.cvtts.audio import CANONICAL_POLICY, encode_float32_wav
from thai_spoof.cvtts.pilot_data import CleanPilotDataset, check_split_disjoint, file_sha256, load_pilot_split


@pytest.fixture
def fake_pilot(tmp_path):
    """Generated signals, not real user recordings; exercise strict manifest audit."""
    base = tmp_path / "data/processed/cvtts/pilot_v1"
    rows = []
    for i in range(80):
        for label in ["bonafide", "spoof"]:
            wave = np.array([0.1 + i / 1000, 0.2 if label == "bonafide" else 0.3], dtype=np.float32)
            content = encode_float32_wav(wave)
            relative = f"data/processed/cvtts/pilot_v1/canonical/clean16k/train/{label}/{i}.wav"
            path = tmp_path / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            source_relative = (f"data/raw/common_voice/{i}.wav" if label == "bonafide"
                               else f"data/processed/cvtts/pilot_v1/native_tts/wayu/train/{i}.wav")
            source = tmp_path / source_relative
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(content)
            rows.append({"sample_id": f"{label}_{i}", "label": label, "split": "train",
                         "source_sample_id": str(i), "source_text_key": str(i),
                         "audio_policy": CANONICAL_POLICY, "audio_path": relative,
                         "source_audio_path": source_relative, "frames": 2,
                         "audio_file_sha256": file_sha256(path), "source_audio_file_sha256": file_sha256(source),
                         "waveform_sha256": hashlib.sha256(wave.astype("<f4").tobytes()).hexdigest()})
    manifest = base / "manifests/wayu_pilot_train_clean16k.csv"
    manifest.parent.mkdir(parents=True)
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return tmp_path, manifest, rows


def test_valid_loader_and_class_order(fake_pilot):
    root, manifest, _ = fake_pilot
    rows, waves = load_pilot_split(root, "train", file_sha256(manifest))
    assert len(rows) == len(waves) == 160
    data = CleanPilotDataset(rows, waves, training=True, seed=42)
    x, label, index = data[0]
    assert x.shape == (64600,) and label == 1 and index == 0
    assert data[1][1] == 0  # spoof, upstream's index 0


def test_corrupt_audio_rejected(fake_pilot):
    root, manifest, rows = fake_pilot
    (root / rows[0]["audio_path"]).write_bytes(b"not original audio")
    with pytest.raises(ValueError, match="audio hash mismatch"):
        load_pilot_split(root, "train", file_sha256(manifest))


def test_wrong_manifest_hash_rejected(fake_pilot):
    root, _, _ = fake_pilot
    with pytest.raises(ValueError, match="manifest hash mismatch"):
        load_pilot_split(root, "train", "incorrect")


def test_source_audio_changed_rejected(fake_pilot):
    root, manifest, rows = fake_pilot
    (root / rows[0]["source_audio_path"]).write_bytes(b"changed source")
    with pytest.raises(ValueError, match="source path/hash mismatch"):
        load_pilot_split(root, "train", file_sha256(manifest))


def test_test_split_is_never_supported(tmp_path):
    with pytest.raises(ValueError, match="no Test loader"):
        load_pilot_split(tmp_path, "test", "unused")


def test_split_overlap_rejected():
    row = {key: "same" for key in ["sample_id", "source_sample_id", "source_text_key", "audio_file_sha256", "waveform_sha256", "source_audio_file_sha256"]}
    with pytest.raises(ValueError, match="overlap"):
        check_split_disjoint([row], [row])


def test_dataset_length_mismatch_rejected():
    with pytest.raises(ValueError, match="equal lengths"):
        CleanPilotDataset([{}], [], training=False, seed=42)
