FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential git && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ruff.toml mypy.ini /app/
COPY src /app/src
COPY tests /app/tests

RUN pip install --upgrade pip && \
    pip install -e .[dev]

CMD ["pytest", "-q"]


