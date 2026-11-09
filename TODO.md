# TODO / Acceptance Plan — MARL GPU Scheduling V1

**Status:** `[x]` contract-ready primitive | `[ ]` pending implementation. Test marked
`pending` is intentionally skipped, NOT passed. Source: `docs/assignment-source.txt`.

## WP0 / IC0 — BOTH owners (do first)
- [x] C0 central config and C1/C2/C3 dataclasses in `src/gpusched/contracts/shared.py`
- [x] C1 JSON SHA-256 + roundtrip helpers and C2/C3 validators
- [x] Interface `SchedulerPort` / `SimulatorPort` + shadow `clone()` signature
- [x] Initial 6 golden fixtures + mock A ScriptedScheduler, mock B FakeEnvironment
- [ ] **SIGN** exact C2 feature layout, field name/type, normalization/probability order
- [ ] **SIGN** C1/C3 JSON layout and same-time Event semantics; finalize invalid action error
- [ ] Review C0 seeds/substream derivation and l_scale percentile convention
- [ ] Mark signatures complete in `docs/NEEDS-SIGNOFF.md`, bump contract_version if changed

## Người A (Environment), assignment A1–A6 ~24 person-days (estimate only)
- [ ] **A1 / 3d** `sim/models.py`: `Node.allocate()` atomic reserve and `release()`;
  `RuntimeJob` status; `Cluster` aggregation; reject invalid fit/duplicates.
  **Accept** TST01 conservation & TST02 one physical node/job.
- [ ] **A2 / 6d** `sim/events.py`: event heap with stable tie-break priority,
  all completions before arrivals, one sweep/timestamp; `ExecutionManager` release at
  `t_alloc + duration`; C3 event logging; `EventSimulator.clone()` deep-copy ALL state.
  **Accept** TST12 release/time ordering, TST14 no shadow mutation.
- [ ] **A3 / 6d** `sim/queue.py`, `sim/events.py`: snapshot queue sweep,
  globally eligible Gate, `max_defer=5`, `PRIORITY_LOCK`, `UNSCHEDULABLE` (manually
  injected impossible job), attempt state transitions MANAGEMENT -> CLUSTER* -> ALLOCATE;
  visited and max K-1 forwards; INVALID action must not mutate state.
  **Accept** TST03, TST05-06, TST09-11, TST19.
- [ ] **A4 / 5d** `sim/cost.py`, `sim/observations.py`: arrival-only EMA,
  exclude current job queue profile, snapshot p_tilde per attempt, compute ΔFhat,
  ΔLhat using injected L_scale, C_i,n, C*_i; C* sentinel 0/validity flag,
  node/cluster tensor and action masks, `cpu_ram_blocked_ratio` counts in C3.
  **Accept** TST04/TST07/TST08 and 6 manual fixtures.
- [ ] **A5 / 3d** `baselines/policies.py`: Random Valid, First Fit, Best Fit,
  RR Cluster + Best Fit through 2-stage C2 adapter. RR cursor update ONLY on
  SELECT_CLUSTER; no baseline Forward. **Accept** TST16.
- [ ] **A6 / 1d** `calibration/random_valid.py`: Random Valid on training workload,
  collect ΔL, p95(abs ΔL), persist calibrated L_scale, report clip rate.
  **Accept** D1 calibration parity and CI IC2.
- [ ] Add A-side contract golden tests & event log fixture cross-review with B.
- [ ] Run baselines on same workloads after IC2; support debugging/Philly schema if needed.

## Người B (Learning/Workload/Evaluation), assignment B1–B4 ~27 person-days
- [ ] **B1 / 7d** `workload/synthetic.py`: Poisson time, offered load controls
  40/65/85%, GPU {1,2,4}, CPU & RAM independently uniform via stable subseeds,
  synthetic duration 3.0 seconds, C1 file+hash; `workload/philly.py` schema inspect
  (D4 pending), filter successful one-attempt single-node exact GPU 1/2/4,
  preserve observed runtime end-start, scale arrivals only; label synthetic_fill.
  **Accept** TST18 reproducibility, timestamps, no trace data misrepresented.
- [ ] **B2 / 6d** `learning/networks.py`: four unshared encoders, Management Actor &
  Critic, Shared Cluster Actor & Critic, MEAN/MAX pooling, candidate scoring with
  precomputed ΔFhat, masked categorical (train sample/eval argmax), CTDE critics.
  **Accept** TST15 unique param IDs/shared Cluster policy, no illegal action.
- [ ] **B3 / 9d** `learning/rewards.py`, `rollout.py`, `shadow.py`, `trainer.py`,
  `checkpoint.py`: B computes rewards from PlacementResult facts; full JobTrajectory,
  separate on-policy Management/Cluster buffers, mixed discounts (1 intra-job,
  gamma_global inter-job), 128 full macro-steps proposal (not fixed), n-step A2C;
  clone old-policy shadow bootstrap, no real state mutations/stale transitions;
  checkpoint best via validation only. **Accept** TST13, TST14, TST20.
- [ ] **B4 / 5d** `eval/evaluator.py`: common arrival-driven p_eval(t) from C1,
  time-avg F_eval/B4/utilization/load imbalance, wait times, 4GPU metrics,
  allocation success, makespan, forward counts, blocked CPU/RAM ratio across loads.
  Same workload across MARL and 4 baselines; **Accept** TST17.
- [ ] B-side FakeEnvironment + FakeEventLog acceptance fixtures cross-reviewed by A.
- [ ] After IC3: training vs all baselines, plots and report (no new V1 ablations).

## Milestones: 6 weeks rough proposal, not a promise
- [ ] IC0: contract schema & fake mocks pass on both sides
- [ ] IC1: real simulator + baseline C3 + B network forward on real DecisionPoint
- [ ] IC2: one complete episode with A2C, shadow+mixed discounts and 4 baselines
- [ ] IC3: MARL beats Random Valid on simple workload as sanity check
- [ ] P7: multi-seed experiments, report + reproducible provenance

## Decisions superseding old assignment text (§9)
- [x] **1 Reward:** A emits facts, B computes reward from RewardConfig.
- [x] **2 Bootstrap:** use `SimulatorPort.clone()` shadow, NOT stale-discard scheme.
- [x] **3 CPU/RAM:** A logs blocking counts, B graphs; diagnostics only.

## Deferred/NOT V1
- [ ] D4: confirm Philly actual schema/job count before claiming trace experiments
- [ ] R1–R5, heterogeneous nodes, GNN, PPO, parallel env, CPU/RAM fragmentation
