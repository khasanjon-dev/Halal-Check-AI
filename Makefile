.PHONY: help build up down restart logs clean install test

help: ## Show available commands
	@echo "Halal Checker API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build and start containers
	docker compose up --build
	@echo ""
	@echo "✅ Services started!"
	@echo "📚 API Documentation: http://localhost:8000/docs"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "💚 Health Check: http://localhost:8000/health"

up: ## Start containers
	docker compose up -d

down: ## Stop containers
	docker compose down

down_v: ## Stop containers and remove volumes
	docker compose down -v
	rm -f backend/halal_check.db

restart: ## Restart all services
	make down_v && make build

logs: ## Show all logs
	docker compose logs -f

logs-backend: ## Show backend logs
	docker compose logs -f backend

logs-frontend: ## Show frontend logs
	docker compose logs -f frontend

install: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

test: ## Test the API
	@echo "Testing Halal Checker API..."
	@curl -X POST "http://localhost:8000/api/v1/halal-check/analyze" \
		-H "Content-Type: application/json" \
		-d '{"text": "Chicken - 100% Halal", "device_id": "test-123"}' || true

dev: ## Run backend in dev mode
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
