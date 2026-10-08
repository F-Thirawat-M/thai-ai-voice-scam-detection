"""One-factor BatchNorm mode control for the bounded Clean pilot diagnostic."""

from __future__ import annotations

import torch
from torch import nn


BN_TYPES = (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.SyncBatchNorm)


def configure_training_mode(model: nn.Module, mode: str) -> int:
    """Keep dropout in train mode; optionally use stored BN statistics.

    BN affine weights/bias remain trainable. Frozen changes both the statistics
    used to normalize Train activations and running-buffer updates, not just EMA.
    """
    if mode not in {"train", "frozen"}:
        raise ValueError("BatchNorm mode must be train or frozen")
    layers = [module for module in model.modules() if isinstance(module, BN_TYPES)]
    if mode == "frozen" and (not layers or any(not bn.track_running_stats for bn in layers)):
        raise ValueError("frozen mode requires BatchNorm with tracked running statistics")
    model.train()
    if mode == "frozen":
        for bn in layers:
            bn.eval()
    return len(layers)


def snapshot_bn_buffers(model: nn.Module) -> dict[str, torch.Tensor]:
    result = {}
    for name, module in model.named_modules():
        if isinstance(module, BN_TYPES):
            for buffer_name, value in module.named_buffers(recurse=False):
                if value is not None:
                    result[f"{name}.{buffer_name}"] = value.detach().cpu().clone()
    return result


def summarize_bn_changes(before: dict[str, torch.Tensor], after: dict[str, torch.Tensor]) -> dict:
    if before.keys() != after.keys() or not before:
        raise ValueError("missing or mismatched BatchNorm buffers")
    changed = []
    counter_deltas = {}
    for name, original in before.items():
        current = after[name]
        if current.shape != original.shape or current.dtype != original.dtype:
            raise ValueError("BatchNorm buffer shape/dtype changed")
        if not torch.isfinite(current).all():
            raise ValueError("nonfinite BatchNorm buffer")
        if not torch.equal(original, current):
            changed.append(name)
        if name.endswith(".num_batches_tracked"):
            counter_deltas[name] = int(current.item() - original.item())
    return {"buffer_count": len(before), "changed_buffer_count": len(changed),
            "changed_buffer_names": changed, "num_batches_tracked_deltas": counter_deltas}
