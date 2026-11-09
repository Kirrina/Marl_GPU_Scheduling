# IC3 — sanity check before hyperparam tuning

With same workload hash/seeds/config, evaluate trained MARL argmax and Random Valid
on easy synthetic workload. Expect MARL to beat Random Valid in agreed primary metric.
If not, audit pipeline, rewards/masks/advantage before tuning. No extra baselines.
Do NOT claim the experiment succeeded without log and score evidence.
