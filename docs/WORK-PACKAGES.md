# A1–A6 / B1–B4 implementation guide

Reference: `assignment-source.txt` §4/§8/Appendix; **this is the source assignment,
not an invented new ownership split.** Estimated A=24d, B=27d, ~6 weeks (rough).

## Standard module TODO contract

Each function marked TODO has: (1) inputs/units; (2) outputs/side effects;
(3) invariants/fail behavior; (4) TSTxx acceptance ID. The implementer need NOT
understand whole system: open their file + `contracts/shared.py` + corresponding
contract `contracts/C0-C3*.md` + golden fixture, then work only within owner folder.

## A workflow

- A1 `sim/models.py`: Node & RuntimeJob. `can_fit` reference already implemented.
  First implement `allocate/release`, tests for conservation, duplicate rejection.
- A2 `sim/events.py`: real `EventSimulator` with heap and completion before arrival,
  deterministic same-time batch. `clone()` includes event seq and RNG so shadow works.
- A3 `sim/queue.py`, `sim/events.py`: snapshot sweep queue; lock after 5 TRUE defers,
  no artificial retries. Management may select locally infeasible cluster even when
  globally feasible. Forward mask only to other eligible and unvisited clusters.
- A4 `sim/cost.py`: reference EMA/F/L primitives exist, implement node cost/cluster
  summary and DecisionPoints; validated shapes. p_tilde frozen each attempt.
- A5 `baselines/policies.py`: two-call policies. RR pointer update at SELECT_CLUSTER.
- A6 `calibration/random_valid.py`: real training workload only, record p95 and hash.

## B workflow

- B1 `workload/synthetic.py`, `philly.py`: Poisson generator + trace schema
  inspection first (D4). Philly runtime is trace-observed; synthetic=3s.
- B2 `learning/networks.py`: four unshared encoders. Management K scores; Cluster
  M+K masked logits, candidate alloc_delta_f. Torch isolated in B package.
- B3 `learning/{rewards,rollout,shadow,trainer,checkpoint}.py`: pure reward helpers
  implemented; integrate with mocks; n-step cross-job returns, lookahead clone,
  latest/best validation-only checkpoints.
- B4 `eval/evaluator.py`: consume C3 logs and C1 file, independent p_eval.
  Plot CPU/RAM blocked ratio only as diagnostics.

## Cross integration

- A mock `sim/scripted_scheduler.py` drives real A environment without B.
- B mock `learning/fake_environment.py` provides valid Management/Cluster C2 without A.
- Both run golden fixtures. Only replace mocks at IC1/IC2; never import internals.
