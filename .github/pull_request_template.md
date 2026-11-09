## Owner / Task
A1/A2/A3/A4/A5/A6 or B1/B2/B3/B4 or shared IC0: ____

## Contracts changed?
- [ ] NO
- [ ] YES — both owners reviewed + version updated + golden fixtures updated

## Proof
- [ ] `make contracts`
- [ ] `make boundaries`
- [ ] `make check`
- [ ] Relevant TSTxx acceptance tests added (not skipped)
- [ ] TODO.md updated

## Architectural invariants
- [ ] No illegal cross-side import
- [ ] No policy duration leakage
- [ ] A outputs facts and B computes rewards
- [ ] Shadow clone does not mutate actual simulator
