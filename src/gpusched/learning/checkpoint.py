"""B3 — checkpoint provenance + determinism (TST20)."""
from __future__ import annotations
from pathlib import Path


def save_checkpoint(path: str | Path, *, training_state: object, metadata: dict) -> None:
    """TODO B3: save four networks+optimizers, config, seeds, workload hash,
    policy version, torch RNG, experiment provenance. latest and validation-best.
    NEVER choose 'best' using test data. TST20.
    """
    raise NotImplementedError("TODO B3: checkpoint serialization")


def load_checkpoint(path: str | Path):
    """TODO B3: restore all training state or actor weights for argmax evaluation."""
    raise NotImplementedError("TODO B3: checkpoint restore")
