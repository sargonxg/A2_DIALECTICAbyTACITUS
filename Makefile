.PHONY: dev test lint format typecheck seed seed-schema seed-frameworks seed-samples \
        create-admin-key deploy build clean docker-build docker-push publish-ontology \
        sdk-generate sdk-build benchmark help

# ─── Variables ───────────────────────────────────────────────────────────────
PROJECT_ID ?= $(shell gcloud config get-value project 2>/dev/null)
REGION     ?= us-east1
IMAGE_TAG  ?= latest
REGISTRY   ?= $(REGION)-docker.pkg.dev/$(PROJECT_ID)/dialectica

# ─── Development ─────────────────────────────────────────────────────────────

dev: ## Start all services locally with docker-compose
	docker-compose up

dev-build: ## Build and start all services
	docker-compose up --build

dev-down: ## Stop all services
	docker-compose down

dev-logs: ## Follow logs for all services
	docker-compose logs -f

dev-local: ## Start minimal local stack (Neo4j + Redis + API)
	docker compose -f docker-compose.local.yml up --build

dev-local-down: ## Stop minimal local stack
	docker compose -f docker-compose.local.yml down

dev-spanner: ## Start with Spanner emulator (activate spanner profile)
	docker compose --profile spanner up

# ─── Testing ─────────────────────────────────────────────────────────────────

test: ## Run all Python tests
	uv run pytest packages/ -v --tb=short

test-unit: ## Run unit tests only (no integration)
	uv run pytest packages/ -v --tb=short -m "not integration"

test-integration: ## Run integration tests (requires running Spanner emulator)
	uv run pytest packages/ -v --tb=short -m "integration"

test-api: ## Run API tests only
	uv run pytest packages/api/tests/ -v

test-ontology: ## Run ontology package tests
	uv run pytest packages/ontology/tests/ -v

test-graph: ## Run graph package tests
	uv run pytest packages/graph/tests/ -v

test-extraction: ## Run extraction package tests
	uv run pytest packages/extraction/tests/ -v

test-reasoning: ## Run reasoning package tests
	uv run pytest packages/reasoning/tests/ -v

test-web: ## Run Next.js tests
	cd apps/web && npm test

test-e2e: ## Run Playwright E2E tests
	cd apps/web && npm run test:e2e

test-benchmark: ## Run benchmark tests only
	uv run pytest packages/api/tests/test_benchmark.py -v

benchmark: ## Run JCPOA benchmark evaluation via API (requires running server)
	curl -s -X POST http://localhost:8000/v1/admin/benchmark/run \
		-H "Content-Type: application/json" \
		-H "X-API-Key: $${ADMIN_API_KEY:-dev-admin-key-change-in-production}" \
		-d '{"corpus_id":"jcpoa","tier":"standard","include_graph_augmented":true}' | python -m json.tool

# ─── Code Quality ─────────────────────────────────────────────────────────────

lint: ## Run ruff linter
	uv run ruff check packages/

lint-fix: ## Run ruff linter with auto-fix
	uv run ruff check packages/ --fix

format: ## Format code with ruff
	uv run ruff format packages/

typecheck: ## Run mypy type checker
	uv run mypy packages/

typecheck-strict: ## Run mypy in strict mode
	uv run mypy packages/ --strict

tsc: ## TypeScript type check for web app
	cd apps/web && npx tsc --noEmit

web-lint: ## Lint Next.js app
	cd apps/web && npx next lint

quality: lint typecheck ## Run Python quality checks
quality-all: lint typecheck tsc web-lint ## Run all quality checks (Python + TypeScript)
quality-check: lint typecheck ## Alias for quality

# ─── Database & Seed ─────────────────────────────────────────────────────────

seed: ## Load all sample data into Neo4j
	uv run python infrastructure/scripts/seed_sample_data.py

seed-api: ## Load sample data via REST API (tests full stack)
	uv run python infrastructure/scripts/seed_via_api.py

seed-schema: ## Initialize Spanner schema (Spanner only)
	uv run python infrastructure/scripts/init_spanner.py

seed-frameworks: ## Load theory frameworks into database
	uv run python infrastructure/scripts/seed_frameworks.py

create-admin-key: ## Generate and store admin API key
	uv run python infrastructure/scripts/create_admin_key.py

# ─── SDK ──────────────────────────────────────────────────────────────────────

sdk-generate: ## Generate TypeScript SDK from OpenAPI spec
	bash infrastructure/scripts/generate_sdk.sh

sdk-build: sdk-generate ## Generate and build TypeScript SDK
	cd packages/sdk-typescript && npx tsc

# ─── Build ────────────────────────────────────────────────────────────────────

build-api: ## Build API Docker image
	docker build -t $(REGISTRY)/api:$(IMAGE_TAG) -f packages/api/Dockerfile .

build-web: ## Build web Docker image
	docker build -t $(REGISTRY)/web:$(IMAGE_TAG) -f apps/web/Dockerfile apps/web/

build: build-api build-web ## Build all Docker images

docker-push: ## Push images to Artifact Registry
	docker push $(REGISTRY)/api:$(IMAGE_TAG)
	docker push $(REGISTRY)/web:$(IMAGE_TAG)

# ─── Deployment ───────────────────────────────────────────────────────────────

tf-init: ## Initialize Terraform
	cd infrastructure/terraform && terraform init

tf-plan: ## Plan Terraform changes
	cd infrastructure/terraform && terraform plan -var="project_id=$(PROJECT_ID)"

tf-apply: ## Apply Terraform changes
	cd infrastructure/terraform && terraform apply -var="project_id=$(PROJECT_ID)"

tf-destroy: ## Destroy Terraform resources
	cd infrastructure/terraform && terraform destroy -var="project_id=$(PROJECT_ID)"

deploy: ## Deploy API to Cloud Run (requires gcloud auth)
	bash infrastructure/scripts/deploy-cloudrun.sh $(PROJECT_ID) $(REGION)

setup-secrets: ## Store Neo4j Aura credentials in Secret Manager
	bash infrastructure/scripts/setup-secrets.sh $(PROJECT_ID)

# ─── Utilities ────────────────────────────────────────────────────────────────

install: ## Install all Python dependencies via uv
	uv sync --all-packages

install-web: ## Install web app dependencies
	cd apps/web && npm install

install-dev: install install-web ## Install all dependencies including dev tools

publish-ontology: ## Build and publish ontology package to PyPI
	cd packages/ontology && uv build && twine upload dist/*

clean: ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf apps/web/.next apps/web/out

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sort
