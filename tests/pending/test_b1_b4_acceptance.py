"""Pending acceptance tests are SKIPPED, not falsely passed."""
import pytest

@pytest.mark.pending
@pytest.mark.parametrize("task,testids",[
    ("B1","TST18"),("B2","TST15"),
    ("B3","TST13 TST14 TST20"),("B4","TST17"),
])
def test_pending_b_module(task,testids):
    pytest.skip(f"TODO {task}: implement real module + acceptance {testids}")
