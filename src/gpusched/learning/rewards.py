"""B3 + integration #1 — B calculates rewards ONLY from A's PlacementResult facts.

A computes C and event facts; B never computes F or ΔL again. Safety requeue paths
remain dormant in synchronized V1. These pure reward functions are implemented.
"""
from __future__ import annotations
from gpusched.contracts.shared import (
    ActionType, PlacementResult, ResultStatus, RewardConfig,
)


def management_reward(final_allocate: PlacementResult, config: RewardConfig) -> float:
    """R_M=-final_cost-lambda_M*(final != initial). Called AFTER final Allocate."""
    if final_allocate.status != ResultStatus.OK or final_allocate.kind != ActionType.ALLOCATE:
        raise ValueError("Management reward requires a successful ALLOCATE fact")
    if final_allocate.initial_cluster is None or final_allocate.final_cluster is None:
        raise ValueError("A must provide both initial and final cluster")
    if final_allocate.placement_cost is None or config.lambda_management is None:
        raise ValueError("Need placement_cost and RewardConfig.lambda_management")
    return (-final_allocate.placement_cost - config.lambda_management *
            int(final_allocate.final_cluster != final_allocate.initial_cluster))


def cluster_allocate_reward(fact: PlacementResult) -> float:
    """R_C^alloc=-C_i,n. Do NOT subtract C*_i again."""
    if fact.status != ResultStatus.OK or fact.kind != ActionType.ALLOCATE or fact.placement_cost is None:
        raise ValueError("Cluster Allocate reward requires successful ALLOCATE + cost")
    return -fact.placement_cost


def cluster_forward_reward(fact: PlacementResult, config: RewardConfig) -> float:
    """R_C^fwd forced -beta(b^(m-1)-1); proactive -beta*b^(m-1)."""
    if fact.status != ResultStatus.OK or fact.kind != ActionType.FORWARD:
        raise ValueError("Cluster Forward reward requires successful FORWARD fact")
    if fact.forward_index is None or fact.forward_index < 1 or fact.is_forced is None:
        raise ValueError("A must emit m>=1 and is_forced")
    if config.beta is None or config.forward_base_b is None or config.beta <= 0 or config.forward_base_b <= 1:
        raise ValueError("RewardConfig requires beta>0 and b>1 before training")
    x=config.forward_base_b ** (fact.forward_index-1)
    return -config.beta * (x-1 if fact.is_forced else x)
