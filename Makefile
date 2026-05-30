SHELL := /bin/bash

.PHONY: help setup lint lint-python lint-frontend format format-python format-frontend test test-python dev-frontend dev-backend dev-workers up down

help:
	@echo "Common commands:"
	@echo "  make setup          - install local dependencies"
	@echo "  make lint           - run all linters"
	@echo "  make format         - run all formatters"
	@echo "  make test           - run python tests"
	@echo "  make up             - start docker services"
	@echo "  make down           - stop docker services"

setup:
	python -m pip install -r backend/requirements-dev.txt
	cd frontend && npm install
	cd workers && python -m pip install -r requirements-dev.txt

lint: lint-python lint-frontend

lint-python:
	cd backend && ruff check .
	cd backend && black --check .
	cd workers && ruff check .
	cd workers && black --check .

lint-frontend:
	cd frontend && npm run lint

format: format-python format-frontend

format-python:
	cd backend && black . && ruff check --fix .
	cd workers && black . && ruff check --fix .

format-frontend:
	cd frontend && npm run format

test: test-python

test-python:
	cd backend && pytest
	cd workers && pytest

up:
	docker compose up -d

down:
	docker compose down

dev-frontend:
	cd frontend && npm run dev

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-workers:
	cd workers && python -m src.main
