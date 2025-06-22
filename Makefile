# =============================================================================
# Environment Management for Yield Curves Project
# =============================================================================

# Default environment
ENV ?= local

# =============================================================================
# Database Management
# =============================================================================

# Start local PostgreSQL container
db-up:
	@echo "🚀 Starting local PostgreSQL database..."
	docker compose up -d postgres
	@echo "✅ Database is running on localhost:5432"
	@echo "   - Database: yield_curves"
	@echo "   - User: postgres"
	@echo "   - Password: postgres"

# Stop local PostgreSQL container
db-down:
	@echo "🛑 Stopping local PostgreSQL database..."
	docker compose down postgres

# Start local Redis container
redis-up:
	@echo "🚀 Starting local Redis..."
	docker compose up -d redis

# Stop local Redis container
redis-down:
	@echo "🛑 Stopping local Redis..."
	docker compose down redis

# Start all local services (postgres + redis)
services-up: db-up redis-up
	@echo "✅ All local services are running"

# Stop all local services
services-down:
	docker compose down

# =============================================================================
# Application Running
# =============================================================================

# 1. Run app locally using local docker db
run-local:
	@echo "🚀 Running app locally with local database..."
	@$(MAKE) db-up
	@sleep 3
	CONFIG_PATH=settings/local/conf.yml CONFIG__DB__YIELD_CURVES__PASSWORD=postgres python -m src.manage runserver --nostatic

run-gunicorn-local:
	@echo "🚀 Running app locally with gunicorn and local database..."
	@$(MAKE) db-up
	@sleep 3
	CONFIG_PATH=settings/local/conf.yml CONFIG__DB__YIELD_CURVES__PASSWORD=postgres gunicorn src.config.wsgi

# 2. Run app in docker container with local docker db
run-docker:
	@echo "🚀 Running app in Docker with local database..."
	CONFIG_PATH=settings/local/conf.yml docker compose up -d --build web

# 6. Run app locally using production db
run-local-prod:
	@echo "🚀 Running app locally with production database..."
	CONFIG_PATH=settings/prod/conf.yml python -m src.manage runserver

# =============================================================================
# Database Migrations
# =============================================================================

# 3. Run migrations on local docker db
migrate-local:
	@echo "🔄 Running migrations on local database..."
	@$(MAKE) db-up
	@sleep 3
	CONFIG_PATH=settings/local/conf.yml CONFIG__DB__YIELD_CURVES__PASSWORD=postgres python -m src.manage migrate

# 4. Run migrations on production db (with app user)
migrate-prod:
	@echo "🔄 Running migrations on production database..."
	CONFIG_PATH=settings/prod/conf.yml python -m src.manage migrate

# Run migrations on production db (with admin user)
migrate-prod-admin:
	@echo "🔄 Running migrations on production database (admin user)..."
	CONFIG_PATH=settings/admin/conf.yml python -m src.manage migrate

# =============================================================================
# Django Shell Access
# =============================================================================

# 5. Access django shell with admin creds
shell-admin:
	@echo "🐍 Opening Django shell with admin credentials..."
	CONFIG_PATH=settings/admin/conf.yml python -m src.manage shell

# Access django shell with local db
shell-local:
	@echo "🐍 Opening Django shell with local database..."
	@$(MAKE) db-up
	@sleep 3
	CONFIG_PATH=settings/local/conf.yml CONFIG__DB__YIELD_CURVES__PASSWORD=postgres python -m src.manage shell

# Access django shell with production app user
shell-prod:
	@echo "🐍 Opening Django shell with production database (app user)..."
	CONFIG_PATH=settings/prod/conf.yml python -m src.manage shell


# =============================================================================
# Scripts
# =============================================================================

get-data-local:
	CONFIG_PATH=settings/local/conf.yml CONFIG__DB__YIELD_CURVES__PASSWORD=postgres python -m src.manage runscript get_bund_data

get-data-prod:
	CONFIG_PATH=settings/prod/conf.yml python -m src.manage runscript get_bund_data

# =============================================================================
# Testing
# =============================================================================

pytest:
	@echo "🧪 Running tests..."
	CONFIG_PATH=settings/test/conf.yml uv run pytest -v tests/ --ignore=tests/django/

django-test:
	@echo "🧪 Running Django tests..."
	CONFIG_PATH=settings/test/conf.yml python -m src.manage test tests/django/ --verbosity=2

# =============================================================================
# Linting
# =============================================================================

ruff-check:
	@echo "🪄 Running Ruff linting..."
	uv run ruff check .

ruff-fix:
	@echo "🪄 Running Ruff fixing..."
	uv run ruff check . --fix

ruff-format-check:
	@echo "🪄 Running Ruff formatting check..."
	uv run ruff format --check .

ruff-format:
	@echo "🪄 Running Ruff formatting..."
	uv run ruff format .

# =============================================================================
# Utility Commands
# =============================================================================

# Show all available commands
help:
	@echo "🎯 Available commands:"
	@echo ""
	@echo "📊 Database Management:"
	@echo "  db-up           - Start local PostgreSQL container"
	@echo "  db-down         - Stop local PostgreSQL container"
	@echo "  redis-up        - Start local Redis container"
	@echo "  redis-down      - Stop local Redis container"
	@echo "  services-up     - Start all local services"
	@echo "  services-down   - Stop all services"
	@echo ""
	@echo "🚀 Application Running:"
	@echo "  run-local       - Run app locally with local docker db"
	@echo "  run-docker      - Run app in docker with local docker db"
	@echo "  run-local-prod  - Run app locally with production db"
	@echo ""
	@echo "🔄 Database Migrations:"
	@echo "  migrate-local   - Run migrations on local docker db"
	@echo "  migrate-prod    - Run migrations on production db (app user)"
	@echo "  migrate-prod-admin - Run migrations on production db (admin user)"
	@echo ""
	@echo "🐍 Django Shell:"
	@echo "  shell-local     - Django shell with local db"
	@echo "  shell-prod      - Django shell with production db (app user)"
	@echo "  shell-admin     - Django shell with production db (admin user)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test           - Run test suite"
	@echo ""
	@echo "💡 Examples:"
	@echo "  make run-local     # Start local development"
	@echo "  make migrate-local # Run migrations locally"
	@echo "  make shell-admin   # Access admin shell"

# Clean up everything
clean:
	@echo "🧹 Cleaning up..."
	docker compose down -v

.PHONY: help db-up db-down redis-up redis-down services-up services-down
.PHONY: run-local run-docker run-local-prod
.PHONY: migrate-local migrate-prod migrate-prod-admin
.PHONY: shell-local shell-prod shell-admin
.PHONY: test clean

# Default target
.DEFAULT_GOAL := help
