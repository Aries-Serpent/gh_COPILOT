.PHONY: setup test

setup:
	pip install -r requirements-test.txt

test: setup
	pytest
