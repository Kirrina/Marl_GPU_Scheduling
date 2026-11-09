"""A2 — Discrete-event simulator and ExecutionManager.

Priority order at same timestamp: COMPLETIONS -> ARRIVALS -> ONE QUEUE SNAPSHOT SWEEP.
Simulator is passive; the trainer owns the outer loop and calls I1 APIs.
No PyTorch imports. Read-only C2 outward; facts-only C2 results.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterable
from gpusched.contracts.shared import (
    DecisionPoint, NextDecision, PlacementResult, SchedulingAction, WorkloadFile,
    EnvironmentConfig, FragmentationConfig, EventLogRecord
)

class EventPriority(IntEnum):
    COMPLETE = 0
    ARRIVAL = 1
    # queue sweep scheduled ONCE after all events at time t, not one per event

@dataclass(order=True, frozen=True)
class ScheduledEvent:
    time: float
    priority: EventPriority
    sequence_number: int
    job_id: str = field(compare=False)

class ExecutionManager:
    def reserve_and_schedule_completion(self, job_id: str, cluster_id: int,
                                        node_id: int, t_alloc: float) -> ScheduledEvent:
        """TODO A2: use job.duration privately; reserve resources; emit COMPLETE at t_alloc+T.

        Output ScheduledEvent(time=t_alloc+job.duration, priority=COMPLETE).
        Do not leak duration to DecisionPoint. TST12.
        """
        raise NotImplementedError("TODO A2: schedule completion")

    def finish(self, event: ScheduledEvent) -> None:
        """TODO A2: release exactly once; append COMPLETE C3 event with gpu_free_after."""
        raise NotImplementedError("TODO A2: finish execution")

class EventSimulator:
    def __init__(self, workload: WorkloadFile, env: EnvironmentConfig,
                 frag: FragmentationConfig):
        """TODO A2: initialize empty nodes, runtime jobs, event heap, queue, EMA, clock.

        Input C1 verified immutable WorkloadFile; output initialized passive simulator.
        Must not import Learning. One episode consumes exactly its workload jobs.
        """
        raise NotImplementedError("TODO A2: initialize EventSimulator")

    def run_until_next_decision(self) -> NextDecision:
        """TODO A2+A3: drive event timestamps and Gate until C2 DecisionPoint or Terminal.

        Process ALL completions first, ALL new arrivals second, one snapshot sweep.
        Process Gate-only work WITHOUT transitions. Never spin on an unallocated job.
        One open attempt follows MANAGEMENT -> CLUSTER* -> ALLOCATE.
        TST03/TST05/TST09/TST10/TST12.
        """
        raise NotImplementedError("TODO A2/A3: simulator state machine")

    def apply_action(self, action: SchedulingAction) -> PlacementResult:
        """TODO A3: validate current action/mask, transition state, return FACTS only.

        SELECT_CLUSTER: set initial/visited, no allocation.
        FORWARD: destination unvisited + locally eligible; record forced and forward_index.
        ALLOCATE: atomic reserve and completion scheduling; return final placement cost.
        INVALID: no resources, events or queue may be mutated. TST04/TST05/TST06.
        """
        raise NotImplementedError("TODO A3: apply SELECT_CLUSTER/FORWARD/ALLOCATE")

    def clone(self) -> EventSimulator:
        """TODO A2+integration #2: deep-copy FULL deterministic state for shadow lookahead.

        Include time, heap, event sequence counter, runtime jobs, node allocations,
        pending queue + snapshot cursor + PRIORITY_LOCK, EMA and p_tilde snapshot,
        attempt visited/forward state, event log and all RNG states.
        Mutating shadow MUST NOT change real simulator. TST14.
        """
        raise NotImplementedError("TODO A2: full shadow simulator deep clone")

    def event_log(self) -> tuple[EventLogRecord, ...]:
        """TODO A2: return immutable C3 records with timestamps and resource deltas."""
        raise NotImplementedError("TODO A2: event log export")
