.PHONY: create-env setup test lint clean-logs

create-env:
	python scripts/setup_environment.py

setup: create-env
        pip install -r requirements-test.txt

lint:
        ruff format .
        ruff check .

test: setup lint
        pytest tests

clean-logs:
        bash scripts/clean_zero_logs.sh logs
