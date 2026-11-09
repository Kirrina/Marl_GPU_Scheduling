"""A6 — D1 Random Valid calibration, run ONCE on TRAIN workload only.

Stores max(empirical p95(abs(delta_L)), epsilon_L) in FragmentationConfig.
Do not recalibrate on validation or test. No torch, no rewards.
"""
from __future__ import annotations
from typing import Sequence
import math


def nearest_rank_quantile_95(values: Sequence[float]) -> float:
    """Quantile convention PROVISIONAL for IC0 sign-off; use same everywhere."""
    if not values:
        raise ValueError("calibration requires samples")
    ordered=sorted(abs(x) for x in values)
    return ordered[math.ceil(0.95*len(ordered))-1]


def calibrate_l_scale(train_workload_file: str, output_config_file: str) -> float:
    """TODO A6: run baseline Random Valid once on immutable TRAIN workload.

        Input train C1 path and config output path. Capture |ΔL| for each real ALLOCATE.
        Output L_scale=max(p95(abs ΔL),epsilon_L); persist origin='calibrated_random_valid'
        and train workload hash; print clipping fraction for monitoring. TST07/IC2.
        Never use test data to calibrate.
    """
    raise NotImplementedError("TODO A6: Random Valid training-only L_scale calibration")
