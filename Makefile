.PHONY: create-env setup test lint clean-logs clean-build compliance check-requirements

create-env:
	python scripts/setup_environment.py

setup: create-env
	pip install -r requirements-test.txt

lint:
	ruff format .
	ruff check . --exit-zero

test: setup lint
	pytest -q --disable-warnings --maxfail=10 --exitfirst tests

clean-logs:
	bash scripts/clean_zero_logs.sh logs

compliance:
	ruff check . --exit-zero
	pytest -q --disable-warnings --maxfail=10 --exitfirst tests
	python scripts/code_placeholder_audit.py

check-requirements:
	python tools/check_requirements.py

.PHONY: convert-daily-whitepaper
convert-daily-whitepaper:
	python tools/convert_daily_whitepaper.py

clean-build:
	bash scripts/clean_build.sh
