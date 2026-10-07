"""Pilot-only bounded memorization diagnostic; Train subset only."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import torch
from torch import nn


def select_train_pairs(rows: list[dict], pairs: int = 2, seed: int = 42) -> list[int]:
    """Choose source pairs without looking at model scores; independent of row order."""
    if isinstance(pairs, bool) or not isinstance(pairs, int) or pairs < 1:
        raise ValueError("pairs must be a positive integer")
    groups: dict[str, dict[str, int]] = {}
    for index, row in enumerate(rows):
        if row["split"] != "train" or row["label"] not in {"bonafide", "spoof"}:
            raise ValueError("only paired Train bonafide/spoof rows are allowed")
        key = row["source_sample_id"]
        if not key or not row["source_text_key"]:
            raise ValueError("source pair identifiers must be nonblank")
        group = groups.setdefault(key, {})
        if row["label"] in group:
            raise ValueError("duplicate label within source pair")
        group[row["label"]] = index
    if pairs > len(groups):
        raise ValueError("not enough source pairs")
    for group in groups.values():
        if set(group) != {"bonafide", "spoof"}:
            raise ValueError("source pair must contain both labels")
        if rows[group["bonafide"]]["source_text_key"] != rows[group["spoof"]]["source_text_key"]:
            raise ValueError("paired text mismatch")
    keys = sorted(groups)
    chosen = sorted(np.random.default_rng(seed).choice(len(keys), pairs, replace=False).tolist())
    return [groups[keys[k]][label] for k in chosen for label in ["bonafide", "spoof"]]


def _validate_batch(x: torch.Tensor, y: torch.Tensor) -> None:
    if x.ndim != 2 or y.ndim != 1 or len(x) != len(y) or len(y) < 2:
        raise ValueError("expected aligned waveform batch and labels")
    if not torch.isfinite(x).all() or y.dtype != torch.long or set(y.cpu().tolist()) != {0, 1}:
        raise ValueError("finite inputs and both integer labels 0/1 are required")


def evaluate_fixed(model: nn.Module, x: torch.Tensor, y: torch.Tensor, microbatch: int = 2) -> dict:
    _validate_batch(x, y)
    if microbatch < 1:
        raise ValueError("microbatch must be positive")
    model.eval()
    outputs = []
    with torch.inference_mode():
        for start in range(0, len(y), microbatch):
            _, logits = model(x[start:start + microbatch])
            if logits.shape != (len(y[start:start + microbatch]), 2) or not torch.isfinite(logits).all():
                raise RuntimeError("invalid logits")
            outputs.append(logits.cpu())
        logits = torch.cat(outputs)
        labels = y.cpu()
        loss = nn.functional.cross_entropy(logits, labels).item()
        if not np.isfinite(loss):
            raise RuntimeError("nonfinite fixed-batch loss")
        return {"loss": loss, "accuracy": (logits.argmax(1) == labels).float().mean().item(),
                "predictions": logits.argmax(1).tolist(), "logits": logits.tolist()}


def fit_fixed_batch(
    model: nn.Module, x: torch.Tensor, y: torch.Tensor, *, max_updates: int = 100,
    min_updates: int = 20, microbatch: int = 2,
    callback: Callable[[dict], None] | None = None,
) -> tuple[list[dict], torch.optim.Optimizer, bool]:
    """All weights trainable; eval mode disables dropout and BN running updates.

    Eval mode does NOT disable autograd. Accumulate sum CE / entire subset size
    so uneven final microbatches also have correct weight. Stop at checked steps
    once accuracy=100% and CE<=0.1, after at least min_updates; never consult Dev.
    """
    _validate_batch(x, y)
    if not 1 <= min_updates <= max_updates <= 200 or microbatch < 1:
        raise ValueError("invalid diagnostic budget or microbatch")
    model.eval()
    if not all(p.requires_grad for p in model.parameters()):
        raise ValueError("this diagnostic requires all parameters trainable")
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=0.0)
    history = []
    before = evaluate_fixed(model, x, y, microbatch)
    history.append({"update": 0, **before})
    if callback:
        callback(history[-1])
    for step in range(1, max_updates + 1):
        optimizer.zero_grad(set_to_none=True)
        training_loss = 0.0
        for start in range(0, len(y), microbatch):
            _, logits = model(x[start:start + microbatch])
            if logits.shape != (len(y[start:start + microbatch]), 2) or not torch.isfinite(logits).all():
                raise RuntimeError("invalid logits during backward")
            loss = nn.functional.cross_entropy(logits, y[start:start + microbatch], reduction="sum") / len(y)
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite backward loss")
            loss.backward()
            training_loss += loss.item()
        norm = nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        if norm.item() <= 0:
            raise RuntimeError("zero gradients; memorization cannot be checked")
        optimizer.step()
        if any(not torch.isfinite(p).all() for p in model.parameters()):
            raise RuntimeError("nonfinite parameters after update")
        row = {"update": step, "backward_loss": training_loss, "gradient_norm_before_clipping": norm.item()}
        if step % 5 == 0 or step == max_updates:
            row.update(evaluate_fixed(model, x, y, microbatch))
        history.append(row)
        if callback:
            callback(row)
        if step >= min_updates and row.get("accuracy") == 1.0 and row.get("loss", float("inf")) <= 0.1:
            return history, optimizer, True
    return history, optimizer, False
