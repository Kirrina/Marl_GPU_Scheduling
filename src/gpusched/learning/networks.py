"""B2 — A2C neural networks, IC0 contract-first; torch import only on B side.

Four separately instantiated/unshared node encoders:
E_M^A Management Actor; E_M^V Management Critic;
E_C^A shared Cluster Actor; E_C^V shared Cluster Critic.
Cluster Actor/Critic weights shared across all K clusters, NOT across actors vs critics.
No GNN or remaining-time input. TST15.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from gpusched.contracts.shared import DecisionPoint

@dataclass(frozen=True)
class NetworkDimensions:
    node_features: int = 4           # proposed contract, must sign IC0
    cluster_stats: int = 10         # proposed contract, must sign IC0
    job_features: int = 3
    cluster_count: int = 3
    nodes_per_cluster: int = 4
    hidden_dim: int = 64            # PROPOSAL ONLY; tune after IC0, not 'fixed'

class ManagementActor:
    def forward(self, decision: DecisionPoint) -> Any:
        """TODO B2: encode node [K,M,4] -> mean/max pools -> cluster scores K.

        Input C2 MANAGEMENT (all K actions unmasked); output torch Tensor logits[K].
        Must not mask locally ineligible clusters (I1/MASK01). TST15.
        """
        raise NotImplementedError("TODO B2: Management Actor / E_M^A")

class ManagementCritic:
    def forward(self, decision: DecisionPoint) -> Any:
        """TODO B2: separate E_M^V on CTDE global state; output scalar V_M."""
        raise NotImplementedError("TODO B2: Management Critic / E_M^V")

class SharedClusterActor:
    def forward(self, decision: DecisionPoint) -> Any:
        """TODO B2: shared E_C^A, local node candidate scores and Forward scores.

        Input C2 CLUSTER, including node-specific normalized alloc_delta_f[M],
        visited flags, p_tilde and q_j. Output logits over M ALLOCATE + K FORWARD
        masked by alloc_mask/forward_mask. No illegal action probability. TST15.
        """
        raise NotImplementedError("TODO B2: shared Cluster Actor / E_C^A")

class SharedClusterCritic:
    def forward(self, decision: DecisionPoint) -> Any:
        """TODO B2: separate E_C^V on global nodes/cluster + current c_i + visited,
        q_j and job context. c_i already has job-specific eligible/C*_i data.
        Output scalar V_C. No duplicate n_eligible/C* features. TST15.
        """
        raise NotImplementedError("TODO B2: shared Cluster Critic / E_C^V")

class MARLNetworks:
    def __init__(self, dims: NetworkDimensions):
        """TODO B2: instantiate exactly 4 independent encoders; verify unique params.
        No B package may import gpusched.sim.*. TST15.
        """
        raise NotImplementedError("TODO B2: assemble Management+Cluster actor/critic")
