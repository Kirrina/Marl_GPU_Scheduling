"""IC0 mock handoff: A scripted scheduler drives B's fake environment via C2."""
from gpusched.sim.scripted_scheduler import ScriptedScheduler
from gpusched.learning.fake_environment import FakeEnvironment
from gpusched.contracts.shared import TerminalPoint, DecisionType, ActionType


def test_mock_c2_two_stream_adapter():
    simulator=FakeEnvironment()
    scheduler=ScriptedScheduler()
    kinds=[]
    while True:
        d=simulator.run_until_next_decision()
        if isinstance(d,TerminalPoint):
            break
        a=scheduler.select_action(d)
        r=simulator.apply_action(a)
        assert r.status.value=="OK"
        kinds.append(a.kind)
    assert kinds==[ActionType.SELECT_CLUSTER,ActionType.ALLOCATE]
