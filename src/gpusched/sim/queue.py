"""A3 — FCFS-by-examination queue, Gate, PRIORITY_LOCK, UNSCHEDULABLE.

TST03/TST09/TST10/TST11/TST19.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from gpusched.contracts.shared import WorkloadJob
from .models import Node, RuntimeJob

@dataclass
class QueueState:
    waiting: deque[str] = field(default_factory=deque)
    priority_lock_job_id: str | None = None
    # TODO A3: track sweep snapshot and examined IDs to ensure <=1 visit/job/time.

class ManagementGate:
    def globally_eligible(self, job: WorkloadJob, nodes: list[Node]) -> bool:
        """True iff at least one physical node satisfies GPU+CPU+RAM hard constraints."""
        return any(node.can_fit(job) for node in nodes)

    def impossible_even_when_empty(self, job: WorkloadJob, nodes: list[Node]) -> bool:
        """TST11: unschedulable only if no empty node can ever fit job."""
        return not any(node.could_fit_if_empty(job) for node in nodes)

class QueueController:
    def sweep_once(self, now: float, jobs: dict[str, RuntimeJob],
                   state: QueueState, nodes: list[Node]) -> str | None:
        """TODO A3: one finite snapshot sweep at event timestamp, return ready job ID.

        Input current jobs/queue/nodes. Output ready job_id for Management Decision,
        or None if Gate failed/queue empty. IMPORTANT: one sweep may allocate several
        jobs; simulator must resume snapshot where left off after each attempt.
        Eligible job -> Management; no eligible -> tail-requeue and defer_count++
        ONLY if actually moved; single blocked job waits for release without counter.
        At max_defer=5 PRIORITY_LOCK at head: block others until fit/release.
        Unknown job fit even empty -> terminal UNSCHEDULABLE (manual test injection).
        Gate-only operations create NO RL transitions. TST03/TST09/TST10/TST11/TST19.
        """
        raise NotImplementedError("TODO A3: queue sweep/priority lock/snapshot")
