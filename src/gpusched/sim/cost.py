"""A4 — deterministic cost feature primitives (not rewards).

Arrival EMA updates ON NEW ARRIVAL ONLY. Queue distribution excludes current job.
Snapshot p_tilde is fixed for an entire scheduling attempt, including all forwards.
TST07/TST08; see docs/technical-spec-original.md §3.
"""
from __future__ import annotations
import math
from collections import Counter
from typing import Sequence
from gpusched.contracts.shared import GPU_DEMANDS, FragmentationConfig, WorkloadJob
from .models import Node


def initial_gpu_profile() -> tuple[float, float, float]:
    return (1/3, 1/3, 1/3)


def update_arrival_ema(old: Sequence[float], new_gpu_demand: int, alpha: float) -> tuple[float,...]:
    """F01: call only when a new WorkloadJob ARRIVES; NEVER on defer/retry."""
    if new_gpu_demand not in GPU_DEMANDS or not (0 < alpha <= 1):
        raise ValueError("invalid gpu demand or alpha")
    return tuple((1-alpha)*p + alpha*(1 if d==new_gpu_demand else 0)
                 for p,d in zip(old,GPU_DEMANDS))


def queue_profile(excluding_job_id: str, waiting_jobs: Sequence[WorkloadJob],
                  arrival_profile: Sequence[float]) -> tuple[float,...]:
    """F02: exclude current job; fallback to EMA if no other waiting jobs."""
    others=[job for job in waiting_jobs if job.job_id != excluding_job_id]
    if not others:
        return tuple(arrival_profile)
    counts=Counter(job.gpu_req for job in others)
    return tuple(counts[d]/len(others) for d in GPU_DEMANDS)


def combined_profile(arrival_profile: Sequence[float], queue_p: Sequence[float],
                     lambda_queue: float) -> tuple[float,...]:
    """F03: p_tilde; skip queue entirely if empty (queue_profile handles fallback)."""
    if lambda_queue < 0:
        raise ValueError("lambda_queue must be nonnegative")
    return tuple((a+lambda_queue*q)/(1+lambda_queue)
                 for a,q in zip(arrival_profile,queue_p))


def fragmentation(r: int, p_tilde: Sequence[float]) -> float:
    """F04: F(r)=r sum_{d>r} p_tilde[d], 0 <= r <= 4 integer."""
    if not isinstance(r,int) or not 0 <= r <= 4:
        raise ValueError("remaining gpu r must be integer 0..4")
    return r * sum(p for d,p in zip(GPU_DEMANDS,p_tilde) if d > r)


def f_max(p_tilde: Sequence[float]) -> float:
    return max(fragmentation(r,p_tilde) for r in range(5))


def delta_f_hat(gpu_free: int, gpu_req: int, p_tilde: Sequence[float],
                epsilon: float=1e-8) -> float:
    """F05-F07; requires globally eligible allocation candidate, else ValueError."""
    if gpu_req not in GPU_DEMANDS or gpu_req > gpu_free:
        raise ValueError("delta_f only for valid GPU placements")
    df=fragmentation(gpu_free-gpu_req,p_tilde)-fragmentation(gpu_free,p_tilde)
    return df/max(f_max(p_tilde),epsilon)


def load_imbalance(cluster_utilizations: Sequence[float]) -> float:
    """F08: population variance of K GPU utilization fractions."""
    if not cluster_utilizations:
        raise ValueError("K must be positive")
    mu=sum(cluster_utilizations)/len(cluster_utilizations)
    return sum((u-mu)**2 for u in cluster_utilizations)/len(cluster_utilizations)


def delta_l_hat(before: Sequence[float], after: Sequence[float], scale: float) -> float:
    """F09: clip ΔL/L_scale to [-1,1]. D1 inject scale; DO NOT calibrate here."""
    if scale <= 0 or not math.isfinite(scale):
        raise ValueError("L_scale must be finite positive")
    value=(load_imbalance(after)-load_imbalance(before))/scale
    return max(-1.0,min(1.0,value))


def placement_cost(dfhat: float, dlhat: float, weight: float) -> float:
    if not (0 <= weight <= 1):
        raise ValueError("weight must be in [0,1]")
    return (1-weight)*dfhat + weight*dlhat


class CostFeatureCalculator:
    def candidate_costs(self, job: WorkloadJob, nodes: list[Node],
                        p_tilde: tuple[float,...], config: FragmentationConfig):
        """TODO A4: full per-node candidate costs incl ΔL if allocated on that node.

        Input job+all node resources+frozen p_tilde+Config with INJECTED L_scale.
        Output mapping (cluster_id,node_id) -> (ΔFhat, ΔLhat, C), ONLY eligible.
        Reuse across Management/Cluster; DO NOT compute reward here. TST07/TST08.
        """
        raise NotImplementedError("TODO A4: per-node load imbalance and cost features")

    def cluster_best_cost(self, candidates: dict, k: int) -> tuple[tuple[float,...],tuple[bool,...]]:
        """TODO A4: C*_i min eligible, sentinel 0 + validity false if no eligible."""
        raise NotImplementedError("TODO A4: cluster_best_cost and sentinel")
