.PHONY: create-env setup test lint

create-env:
	python scripts/setup_environment.py

setup: create-env
	pip install -r requirements-test.txt

test: setup lint
	pytest

lint:
	flake8 --config=.flake8 .
