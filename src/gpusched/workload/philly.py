"""B1 — Philly trace import. D4 ACTUAL schema/count NOT verified; no invented columns.

IMPORTANT: keep actual observed runtime end-start. Only one successful attempt,
single-node, GPU EXACTLY 1/2/4, valid timestamps. Preserve submitted arrival
(relative, optionally scaled); CPU/RAM are SYNTHETIC D3, explicitly labeled.
Source distribution and filtered job counts must be reported. TST18.
"""
from __future__ import annotations
from pathlib import Path
from gpusched.contracts.shared import WorkloadConfig, SeedConfig, WorkloadFile


def inspect_trace_schema(raw_path: str | Path) -> dict:
    """TODO B1+D4: read actual Philly file, report available columns/attempt nesting.

    Output schema summary including GPU, submitted/start/end timestamp sources.
    Must be performed BEFORE implementing filter. Never assume column names.
    """
    raise NotImplementedError("TODO B1/D4: inspect actual Philly input")


def preprocess_philly(raw_path: str | Path, config: WorkloadConfig,
                      seeds: SeedConfig) -> WorkloadFile:
    """TODO B1: after inspection, filter correct single-node successful one-attempt jobs.

    Filter GPU demand EXACT 1/2/4, valid start<end, valid submit time.
    Relative arrival=(submit-submit_min)/trace_time_scale; runtime=end-start.
    Use independent 'cpu'/'ram' sub-seeds for D3 requirements; no rounding GPU.
    If too few jobs, mark added rows 'synthetic_fill', use duration 3.0s for fill.
    Include before/after filter counts, synthetic fraction, trace scaling in header.
    TST18 + source_label integrity and fixed-immutable output.
    """
    raise NotImplementedError("TODO B1/D4: Philly filtering and conversion")
