.PHONY: create-env setup test

create-env:
	python scripts/setup_environment.py

setup: create-env
	pip install -r requirements-test.txt

test: setup
	pytest
