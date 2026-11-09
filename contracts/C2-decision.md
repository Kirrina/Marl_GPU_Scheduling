# C2 Decision API (A<->B)

Source of truth: `contracts/shared.py::{SimulatorPort, SchedulerPort,
DecisionPoint, SchedulingAction, PlacementResult, TerminalPoint}`.
A implements: `run_until_next_decision()->DecisionPoint|TerminalPoint`,
`apply_action(SchedulingAction)->PlacementResult`, `clone()->SimulatorPort`.
B implements SchedulerPort: `select_action(DecisionPoint)->SchedulingAction`.

`DecisionPoint` common (PROVISIONAL shape per assignment §5.1):
- `decision_type`, `episode_id`, `attempt_id`, `job_id`, `sim_time`;
- `job_features[3]=gpu_req/4,cpu_req/16,ram_req/64`;
- `node_features[K][M][4]=gpu_free/4,cpu_free/16,ram_free/64,running_jobs/4`;
- `cluster_stats[K][10]=h0,h1,h2,h3,h4,u_i,F_i,n_eligible/M,Cbest_or0,v_eligible`;
- `p_tilde[3]` order GPU demand 1,2,4, frozen per attempt.
- Management `action_mask[K]=all True` following Gate; cluster eligibility MUST NOT mask Management.
- Cluster-only: current_cluster, q_j, visited_flags[K], alloc_mask[M],
  alloc_delta_f[M] with invalid=0, forward_mask[K].
- No duration/remaining_time/future end timestamp in DecisionPoint.

SchedulingAction: `SELECT_CLUSTER(cluster_id)`, `FORWARD(cluster_id)` or
`ALLOCATE(node_index within current cluster)`. Forward target unvisited/eligible;
max K-1 hops; bad mask returns INVALID without state mutation.

`PlacementResult`: reward-free facts `status/kind/job_id/attempt_id/attempt_closed`,
`initial_cluster`, `forward_index` (starts 1), `is_forced` (no local alloc node),
`placement_cost`, `delta_f_hat`, `delta_l_hat`, `final_cluster`,`final_node`.
B computes all rewards (integration #1) and builds 2 rollout buffers.

`clone()` required for integration #2: shadow looks ahead using old frozen policies,
no real mutation or shadow transitions. Terminal bootstrap is 0.

Validator: `contracts/validation.py`. TST04-08,TST13-15,TST20.
