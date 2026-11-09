# Integration checkpoints — expected verification

- IC0 week0: A ScriptedScheduler and B FakeEnvironment can both read/produce
  C1/C2/C3. Six golden fixtures independently reviewed, no schema breaks.
- IC1 week3: A real simulator + four baseline C3 logs, B real networks accept C2.
  No actual A2C training required to pass IC1.
- IC2 week4: One complete episode with real SimulatorPort and Learning trainer;
  reward alignment, n-step mixed discounts, shadow clone validated.
- IC3 week5: Check MARL beats Random Valid on easy workload BEFORE large tuning.
- Report week6: multi-seed 40/65/85% workloads, all 4 baselines, full metrics.

**Rough estimates only:** A ~24 person-days, B ~27 person-days, ~6 weeks; not a
commitment. Source assignment §8. Extra A support for B Philly schema if required.
