"""A5 — Four V1 baselines, EXACTLY; all implement SchedulerPort via C2.

Each baseline uses same A Simulator/Gate/queue as MARL. Baselines MAY preselect
placement then return two actions (SELECT_CLUSTER then ALLOCATE). No FORWARD.
RR pointer moves exactly once at SELECT_CLUSTER, not again at ALLOCATE.
TST16 baseline parity (shared A+B).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence
from gpusched.contracts.shared import DecisionPoint, SchedulingAction

@dataclass(frozen=True)
class Candidate:
    cluster_id: int
    node_index: int
    gpu_free_before: int
    gpu_req: int

    @property
    def gpu_remaining(self) -> int:
        return self.gpu_free_before - self.gpu_req


def best_fit_candidate(candidates: Sequence[Candidate]) -> Candidate:
    """D2: choose minimum post-placement GPU; tie ascending cluster, node."""
    if not candidates:
        raise ValueError("no eligible candidates")
    return min(candidates, key=lambda c:(c.gpu_remaining,c.cluster_id,c.node_index))


class RandomValid:
    def select_action(self, decision: DecisionPoint) -> SchedulingAction:
        """TODO A5: seeded uniformly among GLOBAL eligible (cluster,node) placements.

        Return SELECT_CLUSTER then ALLOCATE. Use independent baseline_seed.
        Must NOT select Management's unmasked but locally ineligible cluster.
        """
        raise NotImplementedError("TODO A5: RandomValid")

class FirstFit:
    def select_action(self, decision: DecisionPoint) -> SchedulingAction:
        """TODO A5: first eligible pair ascending (cluster_id, node_index); two calls."""
        raise NotImplementedError("TODO A5: FirstFit")

class BestFit:
    def select_action(self, decision: DecisionPoint) -> SchedulingAction:
        """TODO A5: use best_fit_candidate; 2-stage adapter, no Forward."""
        raise NotImplementedError("TODO A5: BestFit")

class RRClusterBestFit:
    def select_action(self, decision: DecisionPoint) -> SchedulingAction:
        """TODO A5: search clusters from RR cursor; first eligible cluster; local BestFit.

        Skip globally invalid clusters. Advance cursor ONCE on SELECT_CLUSTER to
        (chosen_cluster+1)%K; do NOT advance on ALLOCATE. TST16.
        """
        raise NotImplementedError("TODO A5: RR + BestFit")
