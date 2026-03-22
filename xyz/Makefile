.PHONY: install test lint format check clean docs

VENV_BIN = ./venv/bin
export PYTHONPATH = .

install:
	$(VENV_BIN)/pip install -r requirements.txt -r requirements-dev.txt

test:
	$(VENV_BIN)/pytest tests/ -v

test-unit:
	$(VENV_BIN)/pytest tests/unit/ -v

test-integration:
	$(VENV_BIN)/pytest tests/integration/ -v

lint:
	$(VENV_BIN)/ruff check app/ utils/ tests/

format:
	$(VENV_BIN)/ruff format app/ utils/ tests/

check: format
	$(VENV_BIN)/ruff check app/ utils/ tests/ --fix
	$(VENV_BIN)/mypy app/ utils/ --ignore-missing-imports

coverage:
	$(VENV_BIN)/pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

docs:
	$(VENV_BIN)/python scripts/generate_docs.py --section "Manual doc generation"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -name "*.pyc" -delete 2>/dev/null; true
	rm -rf htmlcov/ .coverage
