"""Frozen-BN epoch/evaluation helpers for a bounded pilot, not a main trainer."""

from __future__ import annotations

from contextlib import nullcontext
from itertools import islice
import math

import torch

from .batchnorm import configure_training_mode, snapshot_bn_buffers, summarize_bn_changes


def evaluate_split(model, loader, device, *, preserve_rng: bool = True):
    """Mean CE in eval mode on fixed windows; optional RNG-neutral monitoring.

    Iterating a DataLoader can consume an RNG seed even without shuffling.
    Added Train monitoring/reloads must not perturb the training trajectory.
    Caller must restore Frozen-BN training mode before the next epoch.
    """
    device = torch.device(device)
    devices = [device.index if device.index is not None else torch.cuda.current_device()] if device.type == "cuda" else []
    rng_context = torch.random.fork_rng(devices=devices) if preserve_rng else nullcontext()
    with rng_context, torch.inference_mode():
        model.eval()
        total_loss, scores = 0.0, []
        for x, y, indices in loader:
            _, logits = model(x.to(device))
            if logits.shape != (len(y), 2) or not torch.isfinite(logits).all():
                raise RuntimeError("invalid evaluation logits")
            loss = torch.nn.functional.cross_entropy(logits, y.to(device), reduction="sum")
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite evaluation loss")
            total_loss += loss.item()
            for index, label, pair in zip(indices.tolist(), y.tolist(), logits.cpu().tolist()):
                scores.append({"index": index, "label_index": label, "spoof_logit": pair[0],
                               "bonafide_logit": pair[1], "bonafide_margin": pair[1] - pair[0]})
        if not scores:
            raise ValueError("empty evaluation split")
        return total_loss / len(scores), scores


def train_frozen_epoch(model, loader, optimizer, device, *, accumulation: int = 8) -> dict:
    """One complete epoch, sample-weighted accumulation including a short tail."""
    if isinstance(accumulation, bool) or not isinstance(accumulation, int) or accumulation < 1:
        raise ValueError("accumulation must be a positive integer")
    bn_before = snapshot_bn_buffers(model)
    layers = configure_training_mode(model, "frozen")
    optimizer.zero_grad(set_to_none=True)
    batches, updates, indices_seen = [], [], []
    loss_sum, samples_seen = 0.0, 0
    iterator = iter(loader)
    while group := list(islice(iterator, accumulation)):
        group_samples = sum(len(y) for _, y, _ in group)
        if not group_samples:
            raise ValueError("empty accumulation group")
        for x, y, indices in group:
            _, logits = model(x.to(device))
            if logits.shape != (len(y), 2) or not torch.isfinite(logits).all():
                raise RuntimeError("invalid Train logits")
            loss = torch.nn.functional.cross_entropy(logits, y.to(device))
            if not torch.isfinite(loss):
                raise RuntimeError("nonfinite Train loss")
            (loss * len(y) / group_samples).backward()
            loss_sum += loss.item() * len(y)
            samples_seen += len(y)
            batches.append({"microbatch": len(batches) + 1, "loss": loss.item(), "samples": len(y)})
            indices_seen.extend(indices.tolist())
        norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
        if norm.item() <= 0:
            raise RuntimeError("zero gradients; no learning")
        optimizer.step()
        if any(not torch.isfinite(p).all() for p in model.parameters()):
            raise RuntimeError("nonfinite parameters after update")
        optimizer.zero_grad(set_to_none=True)
        updates.append({"update": len(updates) + 1, "microbatch": len(batches), "samples_seen": samples_seen,
                        "gradient_norm_before_clipping": norm.item(), "learning_rate": optimizer.param_groups[0]["lr"]})
    if not samples_seen:
        raise ValueError("empty Train split")
    audit = summarize_bn_changes(bn_before, snapshot_bn_buffers(model))
    if audit["changed_buffer_count"]:
        raise RuntimeError("Frozen BN buffers changed during training")
    return {"microbatches": batches, "updates": updates, "sample_indices": indices_seen,
            "samples_seen": samples_seen, "train_optimization_mean_loss": loss_sum / samples_seen,
            "batchnorm_audit": {"layer_count": layers, **audit}}


def select_best_trained_epoch(history: list[dict]) -> int:
    """Select by post-epoch Dev CE only, ties go to earliest; epoch 0 is reference."""
    if len(history) < 2 or [row["epoch"] for row in history] != list(range(len(history))):
        raise ValueError("expected baseline epoch 0 followed by consecutive completed epochs")
    if any(not math.isfinite(row["dev_loss"]) or row["dev_loss"] < 0 for row in history):
        raise ValueError("invalid Dev loss")
    return min(history[1:], key=lambda row: (row["dev_loss"], row["epoch"]))["epoch"]


def plot_loss_curve(history: list[dict], output) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    epochs = [row["epoch"] for row in history]
    ax.plot(epochs, [row["train_evaluation_loss"] for row in history], "o-", label="Train (eval mode, fixed windows)")
    ax.plot(epochs, [row["dev_loss"] for row in history], "o-", label="Dev (eval mode, first window)")
    ax.set(title="AASIST Clean pilot: Frozen BN, 3 epochs", xlabel="Epoch (0 = pretrained)", ylabel="Mean cross-entropy loss (lower is better)")
    ax.set_xticks(epochs)
    ax.set_ylim(bottom=0)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)
