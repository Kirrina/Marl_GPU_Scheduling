# Integration tests

`test_fake_c2_adapter.py` proves B FakeEnvironment and A ScriptedScheduler
can hand off via C2 without importing each other's internals (TEST-ONLY cross import).
This is **NOT** evidence that real EventSimulator or MARL A2C is implemented.
IC1, IC2, IC3 tests remain pending in TODO.md.
