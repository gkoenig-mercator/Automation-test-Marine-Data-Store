FROM python:3.14-slim

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry install --only main --no-interaction --no-root

COPY src/ ./src/

ENV PYTHONPATH=/app/src

CMD ["poetry", "run", "python", "src/test_availability_data/main.py", "--data-dir", "data", "--max-products", "1"]