"""A4 — produce C2 frozen DecisionPoint: MANAGEMENT or CLUSTER.

PROVISIONAL dimension/order at IC0: node_features [K][M][4], cluster_stats [K][10].
Histogram free GPU h0..h4 divided by M. Use 4 independent neural encoders on B side.
"""
from __future__ import annotations
from gpusched.contracts.shared import DecisionPoint, EnvironmentConfig, WorkloadJob
from .models import Node


def histogram_free_gpus(nodes: list[Node], gpu_capacity: int=4) -> tuple[float,...]:
    """Histogram 0..4 of GPU-free (normalized by number of nodes); pure shared fixture."""
    if not nodes:
        raise ValueError("cluster must contain at least one node")
    return tuple(sum(n.gpu_free==i for n in nodes)/len(nodes) for i in range(gpu_capacity+1))


class ObservationBuilder:
    def build_management(self, *, job: WorkloadJob, config: EnvironmentConfig,
                         attempt_id: int, episode_id: int, sim_time: float) -> DecisionPoint:
        """TODO A4: job normalized fields, node tensor, stats, snapshot p_tilde.

        Output C2 MANAGEMENT with all K action_mask=True (even locally empty).
        Reject nan/inf; validate_decision before returning. TST04/TST08.
        """
        raise NotImplementedError("TODO A4: MANAGEMENT observation")

    def build_cluster(self, *, job: WorkloadJob, config: EnvironmentConfig,
                      current_cluster: int, visited: set[int],
                      forward_count: int, attempt_id: int,
                      episode_id: int, sim_time: float) -> DecisionPoint:
        """TODO A4: C2 CLUSTER obs with alloc_mask, alloc_delta_f and forward_mask.

        Forward target: !=current, unvisited, >=1 eligible node. Max hops K-1.
        q_j=forward_count/(K-1); do NOT confuse visited flag with eligible flag.
        Missing eligible C*_i: sentinel zero+v_eligible=0. TST05/TST06/TST08.
        """
        raise NotImplementedError("TODO A4: CLUSTER observation and masks")
