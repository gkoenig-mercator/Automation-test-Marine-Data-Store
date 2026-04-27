## Project documentation here
.DEFAULT_GOAL := help

# Print help message
help:
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

start-database: ## Start a Postgres database on EDITO as a service
	poetry run python -m deploy.database.start_postgres_database

add-process: ## Add a process on EDITO (use VERSION env var to override)
	poetry run python -m deploy.process.add_process $(if $(EDITO_PROCESS_VERSION),--version $(EDITO_PROCESS_VERSION)) $(if $(CODE_VERSION),--code-version $(CODE_VERSION))

start-process: ## Start a process on EDITO (use PROCESS_ID and VERSION env vars to override)
	poetry run python -m deploy.process.start_process $(if $(VERSION),--version $(VERSION))

run-tests: ## Run tests
	poetry run pytest -v

format: ## Format code with ruff (modifies files in place)
	poetry run ruff format .
	poetry run ruff check --fix .

format-check: ## Check formatting without modifying files
	poetry run ruff format --check .
	poetry run ruff check .

type-check: ## Run type checking with pyright
	poetry run pyright
	
build-image: ## Build the Docker image for the process
	docker build -f src/Dockerfile -t toolbox-catalogue-check:latest .

run-catalogue-check: ## Pass through the catalogue with the Toolbox
	echo "Running catalogue check script..."
	docker run --env-file .env toolbox-catalogue-check:latest


# Create local database
restart-postgres-docker:
	docker restart somedb

delete-postgres-database:
	(docker exec -it somedb psql -U postgres -c "DROP DATABASE IF EXISTS testavailabilitydb;") || true

setup-postgres-docker-locally: delete-postgres-database
# 	(docker stop somedb && docker rm somedb) || true
	docker pull postgres:latest
	docker run -d -p 5432:5432 --name somedb -e POSTGRES_PASSWORD=lolo postgres
	sleep 5 # wait for postgres to start
	${MAKE} create-postgres-database

create-postgres-database:
	docker exec -it somedb psql -U postgres -c "CREATE DATABASE testavailabilitydb;"
