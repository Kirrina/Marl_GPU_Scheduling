"""C1/C2/C3 structural validation; required in mocks, IC0 and CI."""
from __future__ import annotations
from .shared import (
    CONTRACT_VERSION, DecisionPoint, DecisionType, EnvironmentConfig,
    WorkloadFile, EventLogRecord, EventType,
)
import math


def _finite(name: str, values: object) -> None:
    if isinstance(values, (tuple, list)):
        for index, value in enumerate(values):
            _finite(f"{name}[{index}]", value)
    elif isinstance(values, (int, float)) and not isinstance(values, bool):
        if not math.isfinite(values):
            raise ValueError(f"{name} cannot contain nan/inf")


def validate_decision(decision: DecisionPoint, config: EnvironmentConfig) -> None:
    """Verify proposed shape/layout and fundamental masks; never inspect job duration."""
    k, m = config.num_clusters, config.nodes_per_cluster
    if decision.contract_version != CONTRACT_VERSION:
        raise ValueError("C2 contract_version mismatch")
    if len(decision.job_features) != 3 or len(decision.p_tilde) != 3:
        raise ValueError("C2 job_features and p_tilde must each have length 3")
    if len(decision.node_features) != k or any(len(cluster) != m for cluster in decision.node_features):
        raise ValueError("C2 node_features expected [K][M][4]")
    if any(len(node) != 4 for cluster in decision.node_features for node in cluster):
        raise ValueError("C2 node feature dimension must be 4")
    if len(decision.cluster_stats) != k or any(len(row) != 10 for row in decision.cluster_stats):
        raise ValueError("C2 cluster_stats expected [K][10]")
    for field_name in ("job_features", "node_features", "cluster_stats", "p_tilde"):
        _finite(field_name, getattr(decision, field_name))
    if abs(sum(decision.p_tilde) - 1.0) > 1e-6 or any(x < 0 for x in decision.p_tilde):
        raise ValueError("p_tilde must be a probability distribution")
    if decision.decision_type == DecisionType.MANAGEMENT:
        if decision.action_mask != (True,) * k:
            raise ValueError("Gate passed: Management mask must allow all clusters")
        if decision.current_cluster is not None or decision.alloc_mask or decision.forward_mask:
            raise ValueError("Management decision cannot include Cluster-only actions")
    else:
        if decision.current_cluster is None or not 0 <= decision.current_cluster < k:
            raise ValueError("Cluster current_cluster missing/out-of-range")
        if len(decision.visited_flags) != k or len(decision.alloc_mask) != m:
            raise ValueError("Cluster visited_flags[K], alloc_mask[M] required")
        if len(decision.forward_mask) != k or len(decision.alloc_delta_f) != m:
            raise ValueError("Cluster forward_mask[K], alloc_delta_f[M] required")
        if decision.action_mask:
            raise ValueError("Cluster uses alloc_mask+forward_mask, not action_mask")
        if decision.q_j is None or not 0 <= decision.q_j <= 1:
            raise ValueError("q_j must be normalized to [0,1]")
        if not decision.visited_flags[decision.current_cluster]:
            raise ValueError("Current cluster must be visited")
        if any(decision.forward_mask[i] and decision.visited_flags[i] for i in range(k)):
            raise ValueError("Cannot forward to visited cluster")
        if not any(decision.alloc_mask) and not any(decision.forward_mask):
            raise ValueError("A globally feasible Cluster decision must have a valid action")
        _finite("alloc_delta_f", decision.alloc_delta_f)
        for valid, value in zip(decision.alloc_mask, decision.alloc_delta_f):
            if not valid and value != 0:
                raise ValueError("Invalid node alloc_delta_f must be 0")
    for row in decision.cluster_stats:
        if row[9] == 0.0 and row[8] != 0.0:
            raise ValueError("C*_i sentinel must be zero when v_eligible=0")


def validate_workload(workload: WorkloadFile) -> None:
    if workload.header.contract_version != CONTRACT_VERSION:
        raise ValueError("C1 contract_version mismatch")
    ids = [job.job_id for job in workload.jobs]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate job_id")
    if [job.arrival_time for job in workload.jobs] != sorted(job.arrival_time for job in workload.jobs):
        raise ValueError("C1 jobs must be sorted by arrival_time")


def validate_event(event: EventLogRecord) -> None:
    if event.contract_version != CONTRACT_VERSION:
        raise ValueError("C3 contract_version mismatch")
    _finite("time", event.time)
    if event.time < 0:
        raise ValueError("event.time must be >= 0")
    if event.event_type in (EventType.ALLOCATE, EventType.COMPLETE):
        if event.cluster_id is None or event.node_id is None or event.gpu_free_after is None:
            raise ValueError("ALLOCATE/COMPLETE require cluster/node/gpu_free_after")
    if event.event_type == EventType.DEFER and event.defer_count is None:
        raise ValueError("DEFER requires defer_count")
    if event.event_type in (EventType.ARRIVAL, EventType.DEFER,
                            EventType.ALLOCATE, EventType.UNSCHEDULABLE):
        if event.queue_len is None or event.queue_len_by_gpu is None:
            raise ValueError("Queue-changing event requires queue_len + queue_len_by_gpu")
    if event.gpu_eligible_node_count is not None:
        n = event.gpu_eligible_node_count
        b = event.cpu_ram_blocked_node_count
        if n < 0 or b is None or b < 0 or b > n:
            raise ValueError("Invalid CPU/RAM diagnostic counts")
        if n == 0:
            if event.cpu_ram_blocked_ratio is not None:
                raise ValueError("Blocked ratio must be None/N/A when denominator=0")
        elif event.cpu_ram_blocked_ratio is None or abs(event.cpu_ram_blocked_ratio - b/n) > 1e-8:
            raise ValueError("Blocked ratio must equal blocked/gpu_eligible")
