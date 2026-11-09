"""A-side ScriptedScheduler mock to drive A's real simulator BEFORE B is ready.

This mock is not a fifth evaluation baseline. It simply follows C2 masks.
"""
from gpusched.contracts.shared import (
    ActionType, DecisionPoint, DecisionType, SchedulingAction,
)

class ScriptedScheduler:
    def select_action(self, decision: DecisionPoint) -> SchedulingAction:
        if decision.decision_type == DecisionType.MANAGEMENT:
            return SchedulingAction(ActionType.SELECT_CLUSTER,
                                    cluster_id=next(i for i,x in enumerate(decision.action_mask) if x))
        for i, valid in enumerate(decision.alloc_mask):
            if valid:
                return SchedulingAction(ActionType.ALLOCATE,node_index=i)
        for i, valid in enumerate(decision.forward_mask):
            if valid:
                return SchedulingAction(ActionType.FORWARD,cluster_id=i)
        raise AssertionError("Gate-feasible Cluster DecisionPoint must have a valid action")
