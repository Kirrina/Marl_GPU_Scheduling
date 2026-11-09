# Implement owner B: $ARGUMENTS

Read AGENTS.md, `docs/WORK-PACKAGES.md`, `TODO.md`, contracts C0–C3 and
`src/gpusched/contracts/shared.py`. $ARGUMENTS must specify B1..B4.

Only B-owned files; never import real Simulator internals, use SimulatorPort and
FakeEnvironment while A is unavailable. For B3 apply approved reward separation
and shadow lookahead; do not discard stale transitions or use replay.
Write acceptance tests per TST; `make contracts && make boundaries && make check`.
Report implemented behavior, tests, TODO and contract approval needs.
