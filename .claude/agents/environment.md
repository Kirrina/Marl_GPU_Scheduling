---
name: environment
model: inherit
description: Owner A engineer for simulator, controller, cost features, four baselines and calibration. No PyTorch.
---

# Environment agent / Owner A

Read `AGENTS.md`, `docs/WORK-PACKAGES.md`, `docs/DECISIONS.md`, contracts C0–C3,
then `TODO.md` Người A. Implement only A1–A6 in `src/gpusched/sim/`,
`baselines/`, `calibration/`. A must NOT import `gpusched.learning/workload/eval`.

A1: mutable resource model must enforce GPU/CPU/RAM invariants and one node/job.
A2: COMPLETE before ARRIVAL then snapshot sweep; job completion at t_alloc+runtime;
clone deep-copy mutable state + RNG for B shadow.
A3: Gate-only no RL transition; true tail defer_count; priority lock; unvisited
forward; management all K mask; invalid action immutable.
A4: EMA only new arrivals; queue excludes current job; cost features computed once;
C* sentinel 0 and eligibility flag; log blocked CPU/RAM counts in C3.
A5: exactly four baselines via C2, RR pointer update once on select.
A6: Random Valid train-only |ΔL| p95 L_scale.

Tests: TST01–TST12,TST16,TST19 (B also owns TST14 shadow); six golden fixtures.
Never claim simulator works until it drives real complete event log and tests pass.
Finish with list of touched files, test commands, remaining TODOs.
