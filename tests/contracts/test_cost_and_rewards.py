import pytest
from gpusched.sim.cost import (
    initial_gpu_profile, update_arrival_ema, fragmentation, f_max, delta_f_hat,
    combined_profile, queue_profile, load_imbalance, placement_cost,
)
from gpusched.contracts.shared import (
    ActionType, PlacementResult, ResultStatus, RewardConfig, WorkloadJob,
)
from gpusched.learning.rewards import (
    management_reward, cluster_allocate_reward, cluster_forward_reward,
)
from gpusched.eval.metrics import cpu_ram_blocked_ratio, aggregate_blocking, b4_fragmentation_indicator
from gpusched.baselines.policies import Candidate, best_fit_candidate


def test_initial_ema_and_arrival_update_only():
    assert initial_gpu_profile()==pytest.approx((1/3,1/3,1/3))
    assert update_arrival_ema(initial_gpu_profile(),4,0.05)==pytest.approx((0.95/3,0.95/3,0.95/3+0.05))


def test_queue_excludes_current_and_fallback():
    a=(0.2,0.3,0.5)
    only=(WorkloadJob("current",0,2,1,4,3,"synthetic"),)
    assert queue_profile("current",only,a)==a
    p=combined_profile(a,queue_profile("current",only,a),1.0)
    assert p==pytest.approx(a)


def test_f_positive_and_negative_cases():
    p=(0.1,0.1,0.8)
    assert f_max(p)==pytest.approx(2.4)
    assert delta_f_hat(4,4,p)==pytest.approx(0.)
    assert delta_f_hat(4,2,p)==pytest.approx(2/3)
    assert delta_f_hat(3,1,p)==pytest.approx(-1/3)


def test_imbalance_and_placement_cost():
    assert load_imbalance([0,0,1])==pytest.approx(2/9)
    assert placement_cost(0.5,-0.2,0.2)==pytest.approx(0.36)


def test_reward_ownership_cost_fact_only():
    fact=PlacementResult(ResultStatus.OK,ActionType.ALLOCATE,"j",1,True,
           initial_cluster=0,final_cluster=1,final_node=0,placement_cost=0.2)
    conf=RewardConfig(lambda_management=0.1,beta=0.05,forward_base_b=2.0)
    assert management_reward(fact,conf)==pytest.approx(-0.3)
    assert cluster_allocate_reward(fact)==pytest.approx(-0.2)
    forced1=PlacementResult(ResultStatus.OK,ActionType.FORWARD,"j",1,False,
                            forward_index=1,is_forced=True)
    proactive2=PlacementResult(ResultStatus.OK,ActionType.FORWARD,"j",1,False,
                               forward_index=2,is_forced=False)
    assert cluster_forward_reward(forced1,conf)==pytest.approx(0.)
    assert cluster_forward_reward(proactive2,conf)==pytest.approx(-0.1)


def test_diagnostic_is_only_analysis_and_handles_zero_denominator():
    assert cpu_ram_blocked_ratio(8,3)==0.375
    assert cpu_ram_blocked_ratio(0,0) is None
    assert aggregate_blocking([(8,3),(2,1)])==pytest.approx(0.4)
    assert b4_fragmentation_indicator([4,2,2,0])==pytest.approx(4/8)


def test_best_fit_tie_ascending_cluster_then_node():
    items=[Candidate(2,0,4,2),Candidate(1,1,3,1),Candidate(0,2,3,1)]
    assert best_fit_candidate(items)==Candidate(0,2,3,1)
