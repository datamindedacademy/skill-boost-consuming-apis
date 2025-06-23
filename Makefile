.PHONY: install run-api clean benchmark test

AWS_REGION = eu-west-1
AWS_ACCOUNT_ID = 299641483789

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
	uv run -m pytest -v -s

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

# Docker commands
docker-build:
	@echo "Building Docker image for linux/amd64..."
	docker build --platform linux/amd64 -t skill-boost-api api

docker-push:
	@echo "Pushing Docker image to ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	docker tag skill-boost-api:latest $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/skill-boost-api:latest
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/skill-boost-api:latest

# Help command
help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies using uv sync"
	@echo "  make install-dev - Install development dependencies"
	@echo "  make run-api     - Run the API locally"
	@echo "  make benchmark   - Run benchmark tests"
	@echo "  make test        - Run all tests"
	@echo "  make clean       - Clean up generated files and caches"
	@echo "  make docker-build - Build the Docker image"
	@echo "  make docker-push  - Push the Docker image to ECR"
	@echo "  make help        - Show this help message"
