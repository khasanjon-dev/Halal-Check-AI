help: ## Show available commands
	@echo "Halal Checker API - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build and start containers
	docker compose up --build

up: ## Start containers
	docker compose up

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
