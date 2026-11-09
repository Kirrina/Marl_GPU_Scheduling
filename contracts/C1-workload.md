# C1 Workload File (B writes -> A reads)

Format: immutable JSON `{header, jobs}`; authoritative Python:
`contracts/shared.py::WorkloadFile, WorkloadHeader, WorkloadJob`;
`contracts/io.py` writes/reads SHA-256 over canonical JSON excluding content_hash.

Header fields: `workload_id`, `source`, `seed`, `content_hash`,
`trace_time_scale`, `generator_parameters`, `filter_stats`, `contract_version`.
Jobs sorted by arrival_time with unique `job_id`:
`job_id`, `arrival_time`, `gpu_req`, `cpu_req`, `ram_req`, `duration`, `source_label`.
Units seconds, integer GPU/CPU cores, RAM GiB; gpu_req EXACT 1,2,4; duration>0.

- synthetic => Poisson arrivals, CPU/RAM D3 independent, duration **3 seconds**.
- philly => successful one-attempt, single-node, valid timestamps, demand 1/2/4,
  runtime=end-start from trace; arrival=(submitted-t0)/scale, not runtime scaled.
- synthetic_fill => artificially generated, explicitly count in metadata.
- D4 trace schema/data volume NOT checked. Do not hardcode raw column names.
- All 5 schedulers consume one immutable C1 file, same job order/hash.

Acceptance: TST18, mock load/roundtrip and hash mismatch rejection.
