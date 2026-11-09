"""C0+C1+C2+C3 — ONE source of truth for all cross-team types and defaults.

OWNERS: A+B; changes need agreement and contract_version bump.
FIXED decisions: WP0 I1-I4, D1-D3, D5-D6; 3 integration decisions.
PROVISIONAL SIGN-OFF: 4 node features, 10 cluster stats, ordering/dimensional
normalization proposed in user-supplied two-stream assignment §5.1 (not separately ratified).
Do not add 'duration' to DecisionPoint: runtime is only visible to A's Simulator.
No PyTorch import is allowed here. Units: seconds, cores, GiB, whole GPUs.

TODO C0: Both owners sign layout at IC0; if revised, bump CONTRACT_VERSION and fixtures.
TODO C2: Decide the exact handling of invalid actions via PlacementResult(status=INVALID)
         versus raising InvalidAction; in either case A MUST NOT mutate state on invalid.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Literal, TypeAlias
import math

CONTRACT_VERSION = "0.1.0-draft"
GPU_DEMANDS: tuple[int, ...] = (1, 2, 4)
CPU_CHOICES: tuple[int, ...] = (1, 2, 4, 8)
RAM_GIB_CHOICES: tuple[int, ...] = (4, 8, 16, 32)
NODE_FEATURE_ORDER: tuple[str, ...] = (
    "gpu_free_ratio", "cpu_free_ratio", "ram_free_ratio", "running_jobs_per_4"
)
CLUSTER_STAT_ORDER: tuple[str, ...] = (
    "h0", "h1", "h2", "h3", "h4",
    "gpu_utilization", "fragmentation_normalized", "eligible_nodes_ratio",
    "best_cost_or_zero", "is_eligible",
)
PROBABILITY_ORDER: tuple[int, ...] = GPU_DEMANDS


class DecisionType(str, Enum):
    MANAGEMENT = "MANAGEMENT"
    CLUSTER = "CLUSTER"


class ActionType(str, Enum):
    SELECT_CLUSTER = "SELECT_CLUSTER"
    FORWARD = "FORWARD"
    ALLOCATE = "ALLOCATE"


class ResultStatus(str, Enum):
    OK = "OK"
    INVALID = "INVALID"


class EventType(str, Enum):
    ARRIVAL = "ARRIVAL"
    DEFER = "DEFER"
    PRIORITY_LOCK_ON = "PRIORITY_LOCK_ON"
    PRIORITY_LOCK_OFF = "PRIORITY_LOCK_OFF"
    UNSCHEDULABLE = "UNSCHEDULABLE"
    SELECT_CLUSTER = "SELECT_CLUSTER"
    FORWARD = "FORWARD"
    ALLOCATE = "ALLOCATE"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True)
class EnvironmentConfig:
    num_clusters: int = 3
    nodes_per_cluster: int = 4
    gpu_per_node: int = 4
    cpu_per_node: int = 16
    ram_gib_per_node: int = 64
    max_defer: int = 5                     # D5 fixed initial default
    episode_jobs_N: int = 500            # D5 fixed initial default

    @property
    def total_gpus(self) -> int:
        return self.num_clusters * self.nodes_per_cluster * self.gpu_per_node

    def __post_init__(self) -> None:
        for key in ("num_clusters", "nodes_per_cluster", "gpu_per_node",
                    "cpu_per_node", "ram_gib_per_node", "max_defer", "episode_jobs_N"):
            if getattr(self, key) <= 0:
                raise ValueError(f"{key} must be positive")


@dataclass(frozen=True)
class FragmentationConfig:
    alpha_ema: float = 0.05             # D5
    lambda_queue: float = 1.0           # D5
    weight_imbalance: float = 0.2        # TUNE, provisional (not a final optimal value)
    l_scale: float = 1.0                # D1: placeholder ONLY for tests
    l_scale_origin: Literal["placeholder", "calibrated_random_valid"] = "placeholder"
    epsilon_f: float = 1e-8
    epsilon_l: float = 1e-8

    def require_calibrated(self) -> None:
        """Training/val/test MUST call this before run; 1.0 alone is not a valid calibration."""
        if self.l_scale_origin != "calibrated_random_valid":
            raise ValueError("D1: L_scale must be calibrated using Random Valid on TRAIN workload")
        if not math.isfinite(self.l_scale) or self.l_scale <= 0:
            raise ValueError("l_scale must be finite and positive")


@dataclass(frozen=True)
class WorkloadConfig:
    source: Literal["synthetic", "philly", "mixed"] = "synthetic"
    synthetic_duration_seconds: float = 3.0  # D6: never overwrite Philly real runtimes
    philly_use_trace_duration: bool = True
    gpu_demands: tuple[int, ...] = GPU_DEMANDS
    cpu_choices: tuple[int, ...] = CPU_CHOICES   # D3, uniform discrete, independent
    ram_gib_choices: tuple[int, ...] = RAM_GIB_CHOICES
    trace_time_scale: float = 1.0
    offered_load_target: float | None = None    # TUNE: e.g. 0.40, 0.65, 0.85


@dataclass(frozen=True)
class RewardConfig:
    lambda_management: float | None = None   # TUNE: no ratified numeric default
    beta: float | None = None                # TUNE
    forward_base_b: float | None = None      # TUNE; requires >1
    rho_cluster_safety: float | None = None  # dormant safety only, do NOT tune V1
    rho_management_safety: float | None = None


@dataclass(frozen=True)
class TrainingConfig:
    rollout_macro_steps: int = 128         # proposed initial value, NOT fixed design
    n_step_macro_steps: int = 16           # proposed initial value, NOT fixed design
    gamma_global: float | None = None     # TUNE: must be (0,1) before actual training
    gamma_within_job: float = 1.0         # FIXED
    actor_lr: float | None = None         # suggested elsewhere 3e-4, not signed
    critic_lr: float | None = None        # suggested elsewhere 1e-3, not signed
    entropy_coef: float | None = None
    value_coef: float | None = None
    grad_clip_norm: float | None = None
    policy_sampling_in_training: bool = True
    eval_argmax: bool = True


@dataclass(frozen=True)
class EvaluationConfig:
    offered_load_targets: tuple[float, ...] = (0.40, 0.65, 0.85)
    baseline_names: tuple[str, ...] = (
        "random_valid", "first_fit", "best_fit", "rr_cluster_best_fit"
    )
    common_arrival_ema_for_f_eval: bool = True  # K3, NEVER use scheduler queue in eval
    save_latest_and_best: bool = True


@dataclass(frozen=True)
class SeedConfig:
    workload_seed: int = 2026
    network_seed: int = 2027
    policy_seed: int = 2028
    baseline_seed: int = 2029
    # D3: cpu/ram/fill sub-seeds derived from workload_seed and string labels.


@dataclass(frozen=True)
class ExperimentConfig:
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    fragmentation: FragmentationConfig = field(default_factory=FragmentationConfig)
    workload: WorkloadConfig = field(default_factory=WorkloadConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    seeds: SeedConfig = field(default_factory=SeedConfig)


# C1: pure immutable records. Runtime Job (status/defer_count/retry_count) is A's INTERNAL type.
@dataclass(frozen=True)
class WorkloadJob:
    job_id: str
    arrival_time: float
    gpu_req: int
    cpu_req: int
    ram_req: int
    duration: float
    source_label: Literal["synthetic", "philly", "synthetic_fill"]

    def __post_init__(self) -> None:
        if not self.job_id:
            raise ValueError("job_id must not be empty")
        if self.gpu_req not in GPU_DEMANDS:
            raise ValueError("gpu_req must be exactly 1, 2, or 4, never clamped")
        if self.cpu_req <= 0 or self.ram_req <= 0:
            raise ValueError("cpu_req/ram_req must be positive")
        if not math.isfinite(self.arrival_time) or self.arrival_time < 0:
            raise ValueError("arrival_time must be finite and >= 0")
        if not math.isfinite(self.duration) or self.duration <= 0:
            raise ValueError("duration must be finite and > 0")


@dataclass(frozen=True)
class WorkloadHeader:
    workload_id: str
    source: Literal["synthetic", "philly", "mixed"]
    seed: int
    content_hash: str
    trace_time_scale: float = 1.0
    generator_parameters: Mapping[str, Any] = field(default_factory=dict)
    filter_stats: Mapping[str, Any] = field(default_factory=dict)
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class WorkloadFile:
    header: WorkloadHeader
    jobs: tuple[WorkloadJob, ...]


# C2: all mutable state belongs in A; frozen tuple payloads cannot be changed by B.
@dataclass(frozen=True)
class DecisionPoint:
    decision_type: DecisionType
    episode_id: int
    attempt_id: int
    job_id: str
    sim_time: float
    job_features: tuple[float, float, float]                  # normalized gpu/4,cpu/16,ram/64
    node_features: tuple[tuple[tuple[float, ...], ...], ...]  # [K][M][4] PROVISIONAL
    cluster_stats: tuple[tuple[float, ...], ...]            # [K][10] PROVISIONAL
    p_tilde: tuple[float, float, float]                     # demand order (1,2,4)
    action_mask: tuple[bool, ...] = ()                      # MANAGEMENT: K all True
    current_cluster: int | None = None                     # CLUSTER only
    q_j: float | None = None                               # forward_count/(K-1)
    visited_flags: tuple[bool, ...] = ()                    # CLUSTER: K
    alloc_mask: tuple[bool, ...] = ()                       # CLUSTER: M
    alloc_delta_f: tuple[float, ...] = ()                   # CLUSTER: M, invalid=0
    forward_mask: tuple[bool, ...] = ()                     # CLUSTER: K
    contract_version: str = CONTRACT_VERSION


@dataclass(frozen=True)
class SchedulingAction:
    kind: ActionType
    cluster_id: int | None = None        # SELECT_CLUSTER or FORWARD
    node_index: int | None = None       # ALLOCATE; local index within current cluster

    def __post_init__(self) -> None:
        if self.kind in (ActionType.SELECT_CLUSTER, ActionType.FORWARD):
            if self.cluster_id is None or self.node_index is not None:
                raise ValueError(f"{self.kind.value} requires cluster_id, forbids node_index")
        elif self.kind == ActionType.ALLOCATE:
            if self.node_index is None or self.cluster_id is not None:
                raise ValueError("ALLOCATE requires node_index, forbids cluster_id")


@dataclass(frozen=True)
class PlacementResult:
    """Facts, never reward. One result for each action. INVALID must not mutate env."""
    status: ResultStatus
    kind: ActionType
    job_id: str
    attempt_id: int
    attempt_closed: bool
    initial_cluster: int | None = None
    final_cluster: int | None = None
    final_node: int | None = None
    forward_index: int | None = None
    is_forced: bool | None = None
    placement_cost: float | None = None
    delta_f_hat: float | None = None
    delta_l_hat: float | None = None
    error_reason: str | None = None


@dataclass(frozen=True)
class TerminalPoint:
    episode_id: int
    sim_time: float
    reason: str  # all jobs COMPLETED or permanently UNSCHEDULABLE; no pending events


NextDecision: TypeAlias = DecisionPoint | TerminalPoint


@dataclass(frozen=True)
class EventLogRecord:
    time: float
    event_type: EventType
    job_id: str
    attempt_id: int | None = None
    cluster_id: int | None = None
    node_id: int | None = None
    gpu_free_after: int | None = None
    queue_len: int | None = None
    queue_len_by_gpu: tuple[int, int, int] | None = None
    defer_count: int | None = None
    forward_index: int | None = None
    is_forced: bool | None = None
    initial_cluster: int | None = None
    final_cluster: int | None = None
    # integration issue #3: diagnostics; OPTIONAL when event is SELECT_CLUSTER
    gpu_eligible_node_count: int | None = None
    cpu_ram_blocked_node_count: int | None = None
    cpu_ram_blocked_ratio: float | None = None # None/N/A if gpu_eligible count == 0
    contract_version: str = CONTRACT_VERSION


# B-owned learning records; NOT appended for Gate-only events.
@dataclass(frozen=True)
class Transition:
    decision: DecisionPoint
    action: SchedulingAction
    reward: float
    log_prob: float
    value_estimate: float
    discount: float    # 1.0 within job/forward; gamma_global across scheduling attempts
    done: bool
    critic_state: Any = None     # B-owned CTDE encoding, not public C2 observation


@dataclass
class JobTrajectory:
    job_id: str
    attempt_id: int
    management: Transition | None = None
    cluster_steps: list[Transition] = field(default_factory=list)
    completed: bool = False


class SchedulerPort(Protocol):
    def select_action(self, decision: DecisionPoint) -> SchedulingAction:
        """Choose exactly one valid action; no direct resource mutation."""
        ...


class SimulatorPort(Protocol):
    def run_until_next_decision(self) -> NextDecision:
        """Process event/Gate-only work until MANAGEMENT/CLUSTER decision or Terminal."""
        ...

    def apply_action(self, action: SchedulingAction) -> PlacementResult:
        """Validate mask; commit event/resource mutation; return reward-free facts."""
        ...

    def clone(self) -> SimulatorPort:
        """Integration #2: deep clone event heap, jobs, queue, EMA, clock, RNG, etc."""
        ...
