<<<<<<< HEAD
.PHONY: create-env setup test lint clean-logs
=======
.PHONY: create-env setup test lint
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)

create-env:
	python scripts/setup_environment.py

setup: create-env
<<<<<<< HEAD
        pip install -r requirements-test.txt

lint:
	ruff format .
	ruff check . --exit-zero

test: setup lint
        pytest -q --disable-warnings --maxfail=10 --exitfirst tests

clean-logs:
        bash scripts/clean_zero_logs.sh logs
=======
	pip install -r requirements-test.txt

test: setup
	pytest tests
>>>>>>> 072d1e7e (Nuclear fix: Complete repository rebuild - 2025-07-14 22:31:03)
