FROM python:3.14-slim

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --only main --no-root --no-interaction

COPY src/ ./src/

CMD ["poetry", "run", "python", "src/scripts/retrieve_from_describe_test_availability_and_push_in_db.py", "--data-dir", "data", "--max-products", "1"]