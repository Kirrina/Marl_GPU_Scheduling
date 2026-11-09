# Repo-wide instructions for coding agents and humans

1. Source of truth priority: user's assignment `docs/assignment-source.txt` (A1–A6,
   B1–B4, C0–C3, IC0–IC3), agreed V1 `docs/technical-spec-original.md`, then the
   **three newer approved integration decisions** in `docs/DECISIONS.md`.
2. **Read `src/gpusched/contracts/shared.py` FIRST.** Never duplicate cross-team
   enums/config/DTOs in own modules. Use explicit shared import only.
3. Owner A: only `sim/`, `baselines/`, `calibration/`; no Torch or B imports.
   Owner B: only `workload/`, `learning/`, `eval/`; no `sim/`/`baselines/` imports.
4. Every TODO function docstring states inputs, outputs, invariants and test IDs.
   Replace `NotImplementedError` with tested real behavior. Never return fake
   successful data for missing features; mark tests pending until implemented.
5. A computes cost/features; B computes reward from C2 facts; B must never rederive F.
6. At rollout boundary B calls A's `clone()`, uses frozen OLD policies in shadow;
   discard clone then jointly update. Never mutate real sim during bootstrap.
7. For CPU/RAM diagnostic A adds counts to C3 SELECT_CLUSTER events; B plots ratio;
   never change reward/observation/masks.
8. No remaining-time/duration in C2. Management action mask all K true once Gate
   passes. Cluster Forward only eligible unvisited destinations, max K−1 hops.
9. **If change affects `src/gpusched/contracts` or `contracts/`:** open shared
   review, update docs/golden fixtures, bump CONTRACT_VERSION, check CI.
10. After implementing a TODO: add test matching TST ID, update TODO.md,
    run `make contracts && make boundaries && make check`; report scope and remaining TODO.
11. D4 Philly schema is unverified, D1 l_scale=1 only smoke tests; real training
    requires calibrated source. Do not pretend runtime defaults for reward/γ tuned.
12. Do not implement V2 extras or expand the four baselines without permission.
