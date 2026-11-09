"""B3 integration #2 — CHỐT shadow clone at A2C rollout boundary.

Do NOT apply lookahead action on the REAL simulator. Use frozen OLD policy weights
for both actors and critics; after values are read, discard shadow then update
both policies together. TST14 requires exact cloning incl all RNG streams.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from gpusched.contracts.shared import SimulatorPort, DecisionPoint, DecisionType, TerminalPoint, SchedulingAction

class OldPolicyPort(Protocol):
    def sample(self, decision: DecisionPoint) -> SchedulingAction: ...
    def value_management(self, decision: DecisionPoint) -> float: ...
    def value_cluster(self, decision: DecisionPoint) -> float: ...

@dataclass(frozen=True)
class BootstrapValues:
    management: float
    cluster: float


def shadow_bootstrap(real_simulator: SimulatorPort, frozen_policy: OldPolicyPort) -> BootstrapValues:
    """TODO B3: clone and advance to next SAME-POLICY decision for each Critic.

    Input real SimulatorPort + both frozen OLD policies; output V_M(next),V_C(next).
    1) clone entire simulator incl event queue, EMA, queue sweep, RNG states.
    2) shadow.run_until_next_decision(): if true Terminal -> (0,0).
    3) Find MANAGEMENT observation; V_M = old ManagementCritic at this state.
    4) Select MANAGEMENT action in shadow with old Actor only, APPLY on clone.
       Clone/snapshot policy sampling RNG too: real policy RNG must NOT advance.
    5) If necessary process intervening events/decisions with old policy until
       next CLUSTER observation; V_C = old ClusterCritic. No fake next_obs.
    6) No shadow actions/transitions copied to real rollout; discard clone.
    7) Update BOTH policies only after returning bootstrap values.
    Special cases: if one policy has no next decision until true terminal,
       its bootstrap is 0, do not assume next policy decision is immediate.
    Note: sampled shadow cluster state estimates next-state expectation; no
       guarantee that post-update real policy samples the same cluster.
    Test TST14: real state and RNG unchanged; correct policy version; true terminal.
    """
    raise NotImplementedError("TODO B3: Shadow Simulator Clone Lookahead")
