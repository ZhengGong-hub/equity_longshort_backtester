PY = python
PIP = pip

.PHONY: install lint test format typecheck precommit build

install:
	uv venv || true
	uv pip install -e .[dev]
	pre-commit install

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src

test:
	pytest -q

precommit:
	pre-commit run --all-files




