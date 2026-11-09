"""A1 — Resource domain model. ONLY this side may mutate state.

TST01: resource conservation, no negative resources, complete only allocated jobs.
TST02: a job uses ONE node; no split and exclusive integer GPU placement.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from gpusched.contracts.shared import WorkloadJob, EnvironmentConfig

class JobStatus(str, Enum):
    NEW = "NEW"
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    UNSCHEDULABLE = "UNSCHEDULABLE"

@dataclass
class RuntimeJob:
    spec: WorkloadJob
    status: JobStatus = JobStatus.NEW
    defer_count: int = 0                # only TRUE tail requeue, never Gate-only wait
    retry_count: int = 0                # only failed RL attempt; dormant safety V1
    allocated_cluster: int | None = None
    allocated_node: int | None = None
    allocation_time: float | None = None

@dataclass
class Node:
    cluster_id: int
    node_id: int
    gpu_capacity: int
    cpu_capacity: int
    ram_gib_capacity: int
    gpu_free: int
    cpu_free: int
    ram_gib_free: int
    running_job_ids: set[str] = field(default_factory=set)

    @classmethod
    def empty(cls, cluster_id: int, node_id: int, config: EnvironmentConfig) -> Node:
        return cls(cluster_id,node_id,config.gpu_per_node,config.cpu_per_node,
                   config.ram_gib_per_node,config.gpu_per_node,config.cpu_per_node,
                   config.ram_gib_per_node)

    def can_fit(self, job: WorkloadJob) -> bool:
        """A1 reference: ALL GPU/CPU/RAM must fit same node; GPU exclusive integers."""
        return (self.gpu_free >= job.gpu_req and self.cpu_free >= job.cpu_req
                and self.ram_gib_free >= job.ram_req)

    def could_fit_if_empty(self, job: WorkloadJob) -> bool:
        return (self.gpu_capacity >= job.gpu_req and self.cpu_capacity >= job.cpu_req
                and self.ram_gib_capacity >= job.ram_req)

    def assert_invariants(self) -> None:
        for name, free, capacity in (("gpu",self.gpu_free,self.gpu_capacity),
                                      ("cpu",self.cpu_free,self.cpu_capacity),
                                      ("ram",self.ram_gib_free,self.ram_gib_capacity)):
            if not 0 <= free <= capacity:
                raise AssertionError(f"Node {self.cluster_id}/{self.node_id}: invalid {name}")

    def allocate(self, job: WorkloadJob) -> None:
        """TODO A1: make atomic and record ownership; reject duplicate or infeasible job.

        Input: immutable WorkloadJob. Output: None; decrement GPU/CPU/RAM exactly once.
        Error: ValueError, with NO mutation if infeasible. TST01/TST02.
        """
        raise NotImplementedError("TODO A1: atomic resource allocation")

    def release(self, job: WorkloadJob) -> None:
        """TODO A1: reverse resources for same running job exactly once, then assert invariants.

        Input: WorkloadJob from matching completion. Output: None. TST01/TST12.
        """
        raise NotImplementedError("TODO A1: resource release")

@dataclass
class Cluster:
    cluster_id: int
    nodes: list[Node]

    def eligible_indices(self, job: WorkloadJob) -> list[int]:
        return [node.node_id for node in self.nodes if node.can_fit(job)]
