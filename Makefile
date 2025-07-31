.PHONY: create-env setup test lint clean-logs

create-env:
	python scripts/setup_environment.py

setup: create-env
	pip install -r requirements-test.txt

test: setup
        pytest tests

clean-logs:
        bash scripts/clean_zero_logs.sh logs
