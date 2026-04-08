## Project documentation here
.DEFAULT_GOAL := help

# Print help message
help:
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

start-database: ## Start a Postgres database on EDITO as a service
	poetry run python -m deploy.database.start_postgres_database

add-process: ## Add a process on EDITO (use VERSION env var to override)
	poetry run python -m deploy.process.add_process $(if $(VERSION),--version $(VERSION))

start-process: ## Start a process on EDITO (use PROCESS_ID and VERSION env vars to override)
	poetry run python -m deploy.process.start_process $(if $(VERSION),--version $(VERSION))

run-tests: ## Run tests
	poetry run pytest -v
