"""Public structure must not expose private data, weights or run artifacts."""

from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def git_executable():
    executable = shutil.which("git")
    if executable is None or not (ROOT / ".git").exists():
        pytest.skip("Git working tree required for ignore-policy regression checks")
    return executable


def ignored_paths(git_executable, paths):
    result = subprocess.run(
        [git_executable, "check-ignore", "--no-index", "--stdin", "-z"],
        cwd=ROOT, input=("\0".join(paths) + "\0").encode("utf-8"),
        capture_output=True, check=False,
    )
    assert result.returncode in (0, 1), result.stderr
    return {path for path in result.stdout.decode("utf-8").split("\0") if path}


def test_private_payload_remains_ignored(git_executable):
    # Synthetic filenames only; do not enumerate or publish actual speaker/clip IDs.
    paths = [
        "data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/clips/example.mp3",
        "data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/validated.tsv",
        "data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/README.md",
        "data/raw/noise/example.wav",
        "data/processed/cvtts/pilot_v1/canonical/clean16k/train/bonafide/example.wav",
        "data/processed/cvtts/pilot_v1/native_tts/wayu/dev/example.wav",
        "data/processed/cvtts/pilot_v1/manifests/wayu_pilot_train_clean16k.csv",
        "data/processed/cvtts/pilot_v1/qc/canonical_audio/example.json",
        "data/processed/cvtts/pilot_v1/qc/README.md",
        "data/processed/cvtts/future_version/manifests/example.csv",
        "checkpoints/aasist/AASIST.pth",
        "checkpoints/rawnet2/pre_trained_DF_RawNet2.pth",
        "checkpoints/tts/wayu-paxa-tts-edge/revision/config.json",
        "checkpoints/tts/wayu-paxa-tts-edge/revision/README.md",
        "results/pilot/aasist_clean_smoke/example/last.pt",
        "results/pilot/aasist_clean_smoke/example/dev_scores.csv",
        "results/pilot/rawnet2/example/run.json",
        "results/pilot/rawnet2/example/README.md",
        "results/pilot/share/example.zip",
        "results/pilot/share/example.zip.sha256",
        "results/research/example/run.json",
        "experiments/pilot/notebooks/outputs/example.executed.ipynb",
        "experiments/pilot/notebooks/outputs/README.md",
        "_pilot_handoff/checksums.json",
    ]
    assert ignored_paths(git_executable, paths) == set(paths)


def test_only_intentional_public_placeholders_are_visible(git_executable):
    paths = [
        "data/raw/common_voice/README.md",
        "data/raw/common_voice/cv-corpus-27.0-2026-09-11/th/clips/.gitkeep",
        "data/raw/noise/README.md",
        "data/processed/cvtts/pilot_v1/README.md",
        "data/processed/cvtts/pilot_v1/manifests/.gitkeep",
        "data/processed/cvtts/pilot_v1/canonical/clean16k/train/spoof/.gitkeep",
        "data/processed/cvtts/pilot_v1/native_tts/wayu/dev/.gitkeep",
        "data/processed/cvtts/pilot_v1/qc/canonical_audio/.gitkeep",
        "checkpoints/README.md", "checkpoints/aasist/README.md",
        "checkpoints/rawnet2/README.md", "checkpoints/tts/README.md",
        "checkpoints/tts/wayu-paxa-tts-edge/.gitkeep",
        "results/README.md", "results/pilot/aasist_clean_smoke/README.md",
        "results/pilot/aasist_overfit_check/README.md",
        "results/pilot/rawnet2/README.md", "results/pilot/share/README.md",
        "experiments/pilot/notebooks/outputs/.gitkeep",
    ]
    assert all((ROOT / path).is_file() for path in paths)
    assert ignored_paths(git_executable, paths) == set()
