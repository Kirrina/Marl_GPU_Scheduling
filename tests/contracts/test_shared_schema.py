import pytest
from gpusched.contracts.shared import (
    CONTRACT_VERSION, GPU_DEMANDS, EnvironmentConfig, FragmentationConfig,
    WorkloadConfig, WorkloadJob, ActionType, SchedulingAction, ResultStatus,
    PlacementResult, DecisionType, TerminalPoint,
)
from gpusched.contracts.validation import validate_decision
from gpusched.learning.fake_environment import FakeEnvironment


def test_d5_d6_defaults():
    e=EnvironmentConfig(); f=FragmentationConfig(); w=WorkloadConfig()
    assert (e.max_defer,e.episode_jobs_N,f.alpha_ema,f.lambda_queue)==(5,500,0.05,1.0)
    assert w.synthetic_duration_seconds==3.0
    assert e.total_gpus==48
    assert GPU_DEMANDS==(1,2,4)


def test_d1_training_rejects_uncalibrated_l_scale():
    with pytest.raises(ValueError,match="calibrated"):
        FragmentationConfig().require_calibrated()
    FragmentationConfig(l_scale=0.4,l_scale_origin="calibrated_random_valid").require_calibrated()


def test_one_workload_job_has_duration_but_C2_decision_does_not():
    job=WorkloadJob("j",0,1,2,4,3.0,"synthetic")
    d=FakeEnvironment().run_until_next_decision()
    assert job.duration==3.0
    assert not hasattr(d,"duration")
    assert "duration" not in d.__dataclass_fields__
    assert d.contract_version==CONTRACT_VERSION


def test_management_all_k_unmasked_after_gate():
    d=FakeEnvironment().run_until_next_decision()
    assert d.decision_type==DecisionType.MANAGEMENT
    assert d.action_mask==(True,True,True)
    validate_decision(d,EnvironmentConfig())


def test_fake_env_two_phase_contract_and_clone_isolation():
    e=FakeEnvironment(); shadow=e.clone()
    start=e.run_until_next_decision()
    shadow.apply_action(SchedulingAction(ActionType.SELECT_CLUSTER,cluster_id=2))
    assert e.run_until_next_decision()==start
    c=shadow.run_until_next_decision()
    assert c.decision_type==DecisionType.CLUSTER and c.current_cluster==2
    assert c.visited_flags==(False,False,True)
    assert c.forward_mask==(True,True,False)
    assert shadow.apply_action(SchedulingAction(ActionType.ALLOCATE,node_index=0)).attempt_closed
    assert isinstance(shadow.run_until_next_decision(),TerminalPoint)
    assert e.run_until_next_decision().decision_type==DecisionType.MANAGEMENT


def test_invalid_mock_action_must_not_change_state():
    env=FakeEnvironment()
    response=env.apply_action(SchedulingAction(ActionType.ALLOCATE,node_index=0))
    assert response.status==ResultStatus.INVALID
    assert env.run_until_next_decision().decision_type==DecisionType.MANAGEMENT


def test_action_schema_rejects_ambiguous_args():
    with pytest.raises(ValueError):
        SchedulingAction(ActionType.FORWARD,node_index=0)
    with pytest.raises(ValueError):
        SchedulingAction(ActionType.ALLOCATE,cluster_id=0)
