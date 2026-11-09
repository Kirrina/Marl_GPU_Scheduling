"""B1 — synthetic Poisson workload generator.

GPU demand in (1,2,4), CPU independent discrete uniform 1/2/4/8,
RAM independent uniform 4/8/16/32 GiB. Duration D6 = exactly 3 seconds.
Output C1 WorkloadFile with sorted arrival times and hash. TST18.
"""
from __future__ import annotations
from hashlib import sha256
from random import Random
from gpusched.contracts.shared import (
    SeedConfig, WorkloadConfig, EnvironmentConfig, WorkloadFile,
)


def derive_subseed(workload_seed: int, label: str) -> int:
    """D3: stable deterministic sub-stream, independent of Python hash randomization."""
    digest=sha256(f"marl-v1:{workload_seed}:{label}".encode()).digest()
    return int.from_bytes(digest[:8],"big")


def make_workload_rngs(seed: int) -> dict[str, Random]:
    """CPU/RAM/fill draws independent from arrival/GPU draws, all reproducible."""
    return {label:Random(derive_subseed(seed,label))
            for label in ("arrival", "gpu", "cpu", "ram", "fill")}


def arrival_rate_for_load(target_offered_load: float, total_gpus: int,
                          expected_gpu_seconds: float) -> float:
    """rho = lambda * E[G*T] / G_total; NOT actual achieved utilization."""
    if not (0 < target_offered_load < 1) or total_gpus <= 0 or expected_gpu_seconds <= 0:
        raise ValueError("Invalid offered-load parameters")
    return target_offered_load * total_gpus/expected_gpu_seconds


def generate_synthetic(config: WorkloadConfig, environment: EnvironmentConfig,
                       seeds: SeedConfig, n_jobs: int, offered_load: float) -> WorkloadFile:
    """TODO B1: synthesize n jobs with interarrivals Exp(lambda), GPU 1/2/4.

    Input configs+seeds+n_jobs+offered_load. Output immutable C1 WorkloadFile.
    Use make_workload_rngs() streams. CPU/RAM independent discrete uniform; keep
    T_J=3.0s for ALL synthetic jobs, including synthetic_fill. Arrival>=0 sorted,
    exact source_label='synthetic', metadata with lambda and derived sub-seeds.
    Write via contracts.io.write_workload; reuse identical file across 5 schedulers.
    TST18: same seeds -> identical hash; different arrival workloads -> other hash.
    """
    raise NotImplementedError("TODO B1: Poisson synthetic workload generation")
