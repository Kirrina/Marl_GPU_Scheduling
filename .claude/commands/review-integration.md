# Cross-team integration review

Read `docs/DECISIONS.md`, `contracts/`, `AGENTS.md`, `TODO.md`.
Check no B imports sim, no A imports learning; A emits facts not reward; B computes
rewards; clone deep copied real state/RNG and B policy RNG; blocked ratio diagnostic.
Run full tests and report exact missing TST IDs, do not mark pending as passed.
