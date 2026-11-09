# Decision ledger — approved vs proposed

**Approved after the attached two-stream assignment:**

1. **Reward ownership:** A/Environment produces C2 facts including per-placement
   ΔFhat, ΔLhat, C, initial/final cluster, forward ordinal, forced/proactive.
   B/Learning owns RewardConfig-based R_M, R_C alloc/forward. Cost is not copied.
2. **Shadow clone bootstrap:** on complete scheduling-attempt rollout boundary,
   B clones A Simulator full state incl RNG, advances frozen old policies to the next
   SAME-policy DecisionPoints, computes old Critics bootstrap; never writes shadow
   transitions, discards clone, then updates both policies together; true terminal V=0.
   Replaces outdated suggestion to discard stale transitions from assignment §9.1.
3. **CPU/RAM diagnostic:** record `gpu_eligible_node_count` and
   `cpu_ram_blocked_node_count`, ratio=blocked/gpu_eligible, None when denominator 0.
   A writes C3 event data; B aggregates/plots. NO reward/obs/action-mask changes.

**Approved WP0:** I1 passive event Simulator API, I2 Scheduler interface, I3 central
schemas+sim sole mutation authority, I4 independent seeds+same immutable workload.

**Approved D1–D6:**
- D1 CostCalculator receives injected L_scale; test placeholder1.0; REAL train-only
  Random Valid p95(abs ΔL) before training; freeze validation and test.
- D2 Best Fit post-allocation GPU remaining; ascending `(cluster,node)` tie;
  RR rotates across clusters and picks local Best Fit at first eligible cluster.
- D3 CPU independent uniform {1,2,4,8}, RAM independent {4,8,16,32} GiB,
  seeded AFTER filtering Philly; do not claim sampled values are trace CPU/RAM.
- D4 actual Philly schema/count validation DEFERRED; if necessary seeded synthetic
  fill with explicit source_label.
- D5 max_defer=5, N=500, alpha_ema=.05, lambda_queue=1; EMA p0=(1/3,1/3,1/3).
- D6 ALL synthetic duration=3 seconds; authentic Philly duration=end-start.

**Not separately ratified (initial proposals for signing):**
- C2 node_features [K][M][4], cluster_stats [K][10], normalization and layout
  per assignment §5.1; current code validates this DRAFT shape for IC0.
- C1/C3 field serialization choices, sub-seed SHA256 scheme, nearest-rank percentile
  convention, 128 batch/16 n-step values, network hidden_dim 64, numerical reward/γ.
  These do NOT silently become permanent scientific decisions.

**Clarification spotted while building golden fixtures:** For GPU demand=4 on a
4-GPU node, F(4-4)-F(4)=F(0)-F(4)=0 for *every* p_tilde. Thus assignment
fixture #6 cannot test a nonzero sign of ΔF with a 4-GPU allocation alone. Golden
fixture #6 asserts zero for 4GPU AND adds 1/2GPU examples with positive/negative
sign. Requires both owners review at IC0; not a new reward objective.
