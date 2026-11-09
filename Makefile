.PHONY: install check contracts boundaries todo todo-a todo-b status test
install:
	python -m pip install -e ".[dev]"
contracts:
	python -m pytest -q tests/contracts
boundaries:
	python scripts/check_import_boundaries.py
check: boundaries
	python -m pytest -q
status:
	python -m gpusched status
todo:
	python -m gpusched todo
todo-a:
	python -m gpusched todo A
todo-b:
	python -m gpusched todo B
test: check
