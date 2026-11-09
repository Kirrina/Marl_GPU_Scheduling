# V1 non-regression audit

Compare code to `docs/technical-spec-original.md` and `docs/DECISIONS.md`:
GPU {1,2,4} one node; two reward streams, 4 independent encoders; 4 baselines;
Gate no transitions; Queue snapshot and priority lock; D1 calibration only train;
D5/D6; B shadow old-policy bootstrap; CPU/RAM metric only plotting.
Review all mutable state and policy RNG clone behavior; identify incomplete TODOs.
