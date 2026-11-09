"""Pending acceptance tests are SKIPPED, not falsely passed."""
import pytest

@pytest.mark.pending
@pytest.mark.parametrize("task,testids",[
    ("A1","TST01 TST02"),("A2","TST12 TST14"),
    ("A3","TST03 TST05 TST06 TST09 TST10 TST11 TST19"),
    ("A4","TST04 TST07 TST08"),
    ("A5","TST16"),("A6","D1 calibration"),
])
def test_pending_a_module(task,testids):
    pytest.skip(f"TODO {task}: implement real module + acceptance {testids}")
