# IC0 signature checklist — unresolved contract details, NOT already fixed by user

- [ ] C2 exact node_features [K][M][4], normalization and running_jobs/4.
- [ ] C2 cluster_stats [K][10] with order h0..h4,u,F,n_eligible,C*,v_eligible;
      histogram normalization by M; cluster F normalization by M*F_max.
- [ ] C2 action_mask only for MANAGEMENT; alloc_mask/forward_mask for CLUSTER;
      `PlacementResult(status=INVALID)` vs exception on bad mask (no mutation either way).
- [ ] C1 JSON schema/hash field convention, source_label, file format and names.
- [ ] C3 timestamps, event fields, queue_len_by_gpu on every queue-changing event;
      `SELECT_CLUSTER` used for CPU/RAM blocking diagnostics.
- [ ] Sub-seed implementation SHA256('marl-v1:{seed}:{label}'), labels
      arrival/gpu/cpu/ram/fill; per-assignment only 'stable label substream' proposed.
- [ ] p95(abs ΔL) convention (`nearest-rank` current reference helper).
- [ ] RewardConfig lambda_M/beta/b, gamma_global, optimizer hyperparameters set
      before true training; these are TUNE (not constants in specification).
- [ ] Terminal reason and episode metadata, especially no hanging queue after
      last arrival and events drained.
- [ ] First run of contract suite from A mock and B fake env, golden fixture signoff.
- [ ] Python/torch pinning and formatter decisions agreed in team/CI.

Once agreed: set version e.g. `1.0.0` in shared.py; update fixtures and docs.
