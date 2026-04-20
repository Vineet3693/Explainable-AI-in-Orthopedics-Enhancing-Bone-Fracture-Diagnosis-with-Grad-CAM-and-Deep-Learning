# Makefile for Fracture Detection AI

.PHONY: setup test run clean docker-build docker-run lint format help

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
DOCKER = docker
DOCKER_COMPOSE = docker-compose

help:
	@echo "Available commands:"
	@echo "  setup         Install dependencies"
	@echo "  test          Run tests"
	@echo "  run           Run the API locally"
	@echo "  lint          Run linter (flake8)"
	@echo "  format        Format code (black)"
	@echo "  clean         Remove cache files"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Run with Docker Compose"

setup:
	$(PIP) install -r requirements.txt

test:
	$(PYTEST) tests/ -v --cov=src

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

lint:
	flake8 src/ tests/

format:
	black src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

docker-build:
	$(DOCKER) build -t fracture-detection-ai .

docker-run:
	$(DOCKER_COMPOSE) up --build

docker-stop:
	$(DOCKER_COMPOSE) down
