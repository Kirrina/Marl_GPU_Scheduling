# C0 Shared Configuration — A & B

Authoritative Python definitions: `src/gpusched/contracts/shared.py`.
- EnvironmentConfig: 3 clusters, 4 nodes/cluster, 4 GPU/node, 16 CPU/node, 64 GiB RAM/node;
  max_defer 5, episode_jobs_N 500. Topology numeric values are initial tunables.
- FragmentationConfig: alpha_ema .05, lambda_queue 1.0, w~.2 provisional,
  l_scale 1.0 **test ONLY**. Training requires calibration origin.
- WorkloadConfig: synthetic duration 3s; Philly duration start/end trace; D3 CPU/RAM.
- RewardConfig and TrainingConfig: unspecified TUNE values = None until set explicitly.
- EvalConfig: 4 baselines and three offered-load targets, independent p_eval.
- SeedConfig: four independent top-level streams; CPU/RAM/fill substreams labelled.
- Values in `configs/v1.yaml` mirror Python defaults, no silent numeric tuning.
