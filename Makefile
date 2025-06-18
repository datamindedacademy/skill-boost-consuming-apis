.PHONY: install run-api clean

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

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf api/__pycache__
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache

# Help command
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using uv sync"
	@echo "  make run-api    - Run the API locally"
	@echo "  make clean      - Clean up generated files and caches"
	@echo "  make help       - Show this help message"
