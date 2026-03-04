.PHONY: install test run-help

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest -q

run-help:
	python -m muse_csv_cleaner --help
