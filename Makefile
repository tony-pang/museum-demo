.PHONY: build up down restart test test-unit test-integration test-coverage

# Docker Compose Commands
build: 
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

# Testing Commands
test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/test_api tests/test_clients tests/test_db tests/test_etl tests/test_ml -v

test-integration:
	python -m pytest tests/test_integration -v

test-coverage:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
