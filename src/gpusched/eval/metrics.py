"""B4 — evaluator primitives, no simulator internals imported.

Use SAME workload & arrival-driven p_eval for every scheduler, never queue-sensitive
training p_tilde. Reconstruct resource timeline from C3 ALLOCATE/COMPLETE.
Only cpu_ram_blocked_ratio (integration #3) is pure reference implementation here.
"""
from __future__ import annotations


def cpu_ram_blocked_ratio(gpu_eligible_nodes: int,
                          cpu_ram_blocked_nodes: int) -> float | None:
    """Diagnostic only. None -> N/A; NOT a reward or action mask."""
    if gpu_eligible_nodes < 0 or not 0 <= cpu_ram_blocked_nodes <= gpu_eligible_nodes:
        raise ValueError("Invalid blocked-node counts")
    if gpu_eligible_nodes == 0:
        return None
    return cpu_ram_blocked_nodes/gpu_eligible_nodes


def b4_fragmentation_indicator(free_gpus_by_node: list[int], gpu_per_node: int=4) -> float:
    """B4=sum r*1(0<r<4) / (sum r+epsilon). Independent of EMA/queue."""
    if any(r<0 or r>gpu_per_node for r in free_gpus_by_node):
        raise ValueError("Invalid free GPU list")
    return sum(r for r in free_gpus_by_node if 0<r<gpu_per_node)/(sum(free_gpus_by_node)+1e-8)


def aggregate_blocking(records: list[tuple[int,int]]) -> float | None:
    """Aggregate diagnostic as pooled blocked counts (not unweighted mean of ratios).

    No GPU-eligible nodes => N/A. Document sample window in plot caption.
    """
    total_g=sum(g for g,_ in records)
    total_b=sum(b for _,b in records)
    return cpu_ram_blocked_ratio(total_g,total_b)
