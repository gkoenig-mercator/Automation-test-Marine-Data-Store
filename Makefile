## Project documentation here
.DEFAULT_GOAL := help

# Print help message
help:
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

start-database: ## Start a Postgres database on EDITO as a service
	poetry run python deploy/database/start_postgres_database.py

start-process: ## Start a process on EDITO as a process
	poetry run python deploy/process/add_process.py

