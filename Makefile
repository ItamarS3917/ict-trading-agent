# ICT Trading Agent - Development Commands

.PHONY: install dev lint format test coverage run clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make install    - Install production dependencies"
	@echo "  make dev        - Install development dependencies"
	@echo "  make lint       - Run Ruff linter"
	@echo "  make format     - Format code with Ruff"
	@echo "  make test       - Run tests"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make run        - Start Streamlit app"
	@echo "  make clean      - Remove cache files"

# Install production dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Install development dependencies
dev:
	pip install -r requirements-dev.txt
	pip install -e .

# Run linter
lint:
	ruff check .
	ruff format --check .

# Format code
format:
	ruff check --fix .
	ruff format .

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
coverage:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Start Streamlit app
run:
	streamlit run src/main.py

# Clean cache files
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	@echo "Cache files cleaned"
