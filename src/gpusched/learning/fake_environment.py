"""B-side C2 MOCK for IC0. NOT a real GPU simulator, not used for experiments.

It validates two-stream handoff and B training wiring without A's queue/Gate.
One fake job, one fake MANAGEMENT -> CLUSTER -> ALLOCATE decision chain.
"""
from __future__ import annotations
from copy import deepcopy
from gpusched.contracts.shared import (
    ActionType, DecisionPoint, DecisionType, EnvironmentConfig, NextDecision,
    PlacementResult, ResultStatus, SchedulingAction, TerminalPoint
)
from gpusched.contracts.validation import validate_decision

class FakeEnvironment:
    def __init__(self, config: EnvironmentConfig=EnvironmentConfig()):
        self.config=config
        self.stage="MANAGEMENT"
        self.cluster: int | None=None
        self.initial_cluster: int | None=None
        self.visited: set[int]=set()
        self.forward_count=0
        self._last_cost=0.0  # dummy, NOT A's actual Cost Calculator

    def _base(self) -> dict:
        k,m=self.config.num_clusters,self.config.nodes_per_cluster
        # Proposed 4+10-dimensional layout. All clusters/nodes are fully free.
        return dict(episode_id=0,attempt_id=0,job_id="fake-0",sim_time=0.0,
                    job_features=(0.25,0.0625,0.0625),
                    node_features=tuple(tuple((1.0,1.0,1.0,0.0) for _ in range(m)) for _ in range(k)),
                    cluster_stats=tuple((0.,0.,0.,0.,1.,0.,0.,1.,0.,1.) for _ in range(k)),
                    p_tilde=(1/3,1/3,1/3))

    def run_until_next_decision(self) -> NextDecision:
        if self.stage=="DONE":
            return TerminalPoint(episode_id=0,sim_time=3.0,reason="mock complete")
        base=self._base()
        if self.stage=="MANAGEMENT":
            d=DecisionPoint(decision_type=DecisionType.MANAGEMENT, action_mask=(True,)*self.config.num_clusters,**base)
        else:
            k,m=self.config.num_clusters,self.config.nodes_per_cluster
            d=DecisionPoint(decision_type=DecisionType.CLUSTER,current_cluster=self.cluster,
                 q_j=self.forward_count/max(1,k-1),visited_flags=tuple(i in self.visited for i in range(k)),
                 alloc_mask=(True,)*m, alloc_delta_f=(0.,)*m,
                 forward_mask=tuple(i not in self.visited for i in range(k)),**base)
        validate_decision(d,self.config)
        return d

    def apply_action(self, action: SchedulingAction) -> PlacementResult:
        if self.stage=="MANAGEMENT" and action.kind==ActionType.SELECT_CLUSTER:
            if action.cluster_id is None or not 0 <= action.cluster_id < self.config.num_clusters:
                return PlacementResult(ResultStatus.INVALID,action.kind,"fake-0",0,False,error_reason="cluster out of range")
            self.cluster=action.cluster_id
            self.initial_cluster=self.cluster
            self.visited={self.cluster}
            self.stage="CLUSTER"
            return PlacementResult(ResultStatus.OK,action.kind,"fake-0",0,False,initial_cluster=self.cluster)
        if self.stage=="CLUSTER" and action.kind==ActionType.FORWARD:
            if action.cluster_id is None or action.cluster_id in self.visited or not 0 <= action.cluster_id < self.config.num_clusters:
                return PlacementResult(ResultStatus.INVALID,action.kind,"fake-0",0,False,error_reason="visited/out of range")
            self.forward_count+=1
            self.visited.add(action.cluster_id)
            self.cluster=action.cluster_id
            return PlacementResult(ResultStatus.OK,action.kind,"fake-0",0,False,
                                   initial_cluster=self.initial_cluster,forward_index=self.forward_count,is_forced=False)
        if self.stage=="CLUSTER" and action.kind==ActionType.ALLOCATE:
            if action.node_index is None or not 0 <= action.node_index < self.config.nodes_per_cluster:
                return PlacementResult(ResultStatus.INVALID,action.kind,"fake-0",0,False,error_reason="node out of range")
            self.stage="DONE"
            return PlacementResult(ResultStatus.OK,action.kind,"fake-0",0,True,
                  initial_cluster=self.initial_cluster,final_cluster=self.cluster,
                  final_node=action.node_index,placement_cost=self._last_cost,
                  delta_f_hat=0.,delta_l_hat=0.)
        return PlacementResult(ResultStatus.INVALID,action.kind,"fake-0",0,False,error_reason="wrong stage")

    def clone(self) -> FakeEnvironment:
        return deepcopy(self)
