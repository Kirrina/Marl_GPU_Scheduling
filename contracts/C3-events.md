# C3 Event Log (A writes -> B evaluates)

Types: ARRIVAL, DEFER, PRIORITY_LOCK_ON, PRIORITY_LOCK_OFF, UNSCHEDULABLE,
SELECT_CLUSTER, FORWARD, ALLOCATE, COMPLETE. No reward (B owns reward).

Each JSONL record: `time`, `event_type`, `job_id`, optional `attempt_id`,
`cluster_id`, `node_id`, `gpu_free_after`, `queue_len`, `queue_len_by_gpu[3]`,
`defer_count`, `forward_index`, `is_forced`, `initial_cluster`,`final_cluster`.
- ALLOCATE/COMPLETE MUST include cluster_id,node_id,gpu_free_after;
  B reconstructs GPU state for time-weighted metrics.
- Any queue-changing record MUST include queue_len and queue_len_by_gpu.
- DEFER includes actual defer_count. Forward emits forced vs proactive facts.
- D3 diagnostic attached to SELECT_CLUSTER (once per considered job):
  `gpu_eligible_node_count`, `cpu_ram_blocked_node_count`,
  `cpu_ram_blocked_ratio` (null/N/A if no node has enough GPU).
  Do NOT feed diagnostic into reward, mask, Actor or Critic.
- p_eval is calculated from external C1 arrivals, not queue-dependent A p_tilde.

Contract type: `contracts/shared.py::EventLogRecord`.
Reference C3 I/O: `contracts/io.py::write_event_log/read_event_log`.
TST17 event timeline parity; TST12 correct release; no fabricated eval values.
