"""B4 — Event Log C3 -> time-weighted evaluation, TST17.

Metrics to produce EV01–EV10 (source): time-avg F_eval via independent p_eval,
B4, cluster imbalance, GPU utilization, successful allocations, waiting times
including 4 GPU jobs, makespan, 4GPU queue, forward forced/proactive counts,
CPU/RAM blocked ratio. Train sample, val/test argmax, same seeds/workload.
"""
from __future__ import annotations
from pathlib import Path
from gpusched.contracts.shared import EvaluationConfig, EnvironmentConfig

class Evaluator:
    def from_event_log(self, workload_file: str | Path, log_file: str | Path,
                       environment: EnvironmentConfig,
                       evaluation: EvaluationConfig) -> dict:
        """TODO B4: verify workload hash, use external arrivals to produce p_eval(t).

        Reconstruct all node GPU states from C3 ALLOCATE/COMPLETE and initial empty
        config. Integrate F_eval, B4, L and GPU util over SIMULATED TIME (not event count).
        Waiting time=allocation-arrival. Report impossible jobs separately.
        Use blocked counts from SELECT_CLUSTER events; if denominator=0 mark N/A.
        Output report dict for plots + aggregated table; no reward modifications.
        TST17: same external workload -> identical p_eval across MARL and baselines.
        """
        raise NotImplementedError("TODO B4: C3 metrics, time integration, plots")
