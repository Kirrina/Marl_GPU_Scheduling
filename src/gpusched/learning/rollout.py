"""B3 — two ON-POLICY rollout buffers, never historical replay.

- A Management decision happens once per scheduling attempt, reward at terminal ALLOCATE.
- Cluster has 1+ micro-step transitions (FORWARD* then ALLOCATE).
- Gamma 1 within same attempt, gamma_global across scheduling attempts.
- Rollout batch boundary only after COMPLETE attempt, not while forwarding.
- JobTrajectory groups decisions and facts. TST13.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from gpusched.contracts.shared import JobTrajectory, Transition

@dataclass
class ManagementRollout:
    transitions: list[Transition] = field(default_factory=list)

@dataclass
class ClusterRollout:
    transitions: list[Transition] = field(default_factory=list)


def close_job_trajectory(trajectory: JobTrajectory, facts: list, reward_config) -> JobTrajectory:
    """TODO B3: attach terminal Management and each Cluster reward from A facts.

    Inputs: all decisions+facts for an attempt, RewardConfig. Output complete
    JobTrajectory. Must align R_M with final ALLOCATE, Cluster R on each micro-step.
    Gate-only events produce no transitions. TST13.
    """
    raise NotImplementedError("TODO B3: close trajectories and assign rewards")


def n_step_targets(transitions: list[Transition], bootstrap_value: float,
                   n_step: int) -> list[float]:
    """TODO B3: mixed-discount n-step returns and advantages.

    G_t=sum_{j=0}^{n-1}(prod_{k<j} discount_{t+k}) * r_{t+j}
        + prod_{k<n}(discount_{t+k}) * V_{t+n}, unless terminal.
    For cluster: discount=1 on FORWARD within job, gamma_global crossing jobs.
    Use same-policy bootstraps only; Terminal V=0. TST13/TST14.
    """
    raise NotImplementedError("TODO B3: n-step returns")
