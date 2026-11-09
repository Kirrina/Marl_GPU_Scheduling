"""B3 — orchestrates A's SimulatorPort via C2 WITHOUT importing gpusched.sim.

B owns the active loop: run_until_next_decision -> sample -> apply_action,
then rewards, rollouts, shadow bootstrap, joint A2C update. TST13/TST14/TST20.
"""
from __future__ import annotations
from gpusched.contracts.shared import SimulatorPort, ExperimentConfig

class A2CTrainer:
    def __init__(self, config: ExperimentConfig):
        """TODO B3: instantiate networks and separate actor/critic optimizers.

        REQUIRE FragmentationConfig.require_calibrated() before real training.
        Select Adam / entropy / grad clip from TrainingConfig TUNE values.
        Keep Management and Cluster actor/critic weights frozen during collection.
        """
        raise NotImplementedError("TODO B3: initialize A2CTrainer")

    def collect_batch(self, simulator: SimulatorPort):
        """TODO B3: gather N COMPLETE real scheduling macro-steps.

        Scheduling attempt: MANAGEMENT 1 action, CLUSTER 1..K actions.
        Controller Gate-only events absent from policy transitions. Close delayed
        Management reward when Allocate finishes. No update mid-forward.
        Output two independent on-policy rollouts + current real simulator state.
        """
        raise NotImplementedError("TODO B3: collect complete macro-steps")

    def train_one_update(self, simulator: SimulatorPort) -> dict[str,float]:
        """TODO B3: collect -> shadow_bootstrap with old policies -> n-step -> update.

        BOTH networks updated only after shadow is destroyed. Do not replay stale
        transitions or carry-over actions sampled by old policy after update.
        Output diagnostics {loss_actor_M,loss_critic_M,loss_actor_C,loss_critic_C,
        entropy_M,entropy_C,explained_variance_M,explained_variance_C,...}.
        """
        raise NotImplementedError("TODO B3: A2C update")
