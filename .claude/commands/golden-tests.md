# Contract golden tests

Run `python -m pytest -q tests/contracts/test_golden_cases.py`
and `python -m pytest -q tests/contracts`.
Compare scenarios G01–G06 to source §6 and docs/DECISIONS.md clarification about
4GPU ΔF. If a case fails, identify whether the formula, fixture or implementation
is wrong; never update expected value solely to make tests green.
