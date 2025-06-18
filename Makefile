.PHONY: install run-api clean benchmark test

# Default target
all: install

# Install dependencies using uv sync
install:
	@echo "Installing dependencies..."
	uv sync
	cd api && uv sync


# Run the API locally
run-api:
	@echo "Starting API server..."
	cd api && uv run -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run benchmark tests
benchmark: install
	@echo "Running benchmark tests..."
	uv run -m pytest -v

# Run all tests
test: install-dev
	@echo "Running all tests..."
	uv run -m pytest

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf api/__pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf tests/__pycache__
	rm -f device_measurements_*.csv

# Help command
help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies using uv sync"
	@echo "  make install-dev - Install development dependencies"
	@echo "  make run-api     - Run the API locally"
	@echo "  make benchmark   - Run benchmark tests"
	@echo "  make test        - Run all tests"
	@echo "  make clean       - Clean up generated files and caches"
	@echo "  make help        - Show this help message"
