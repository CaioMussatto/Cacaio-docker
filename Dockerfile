FROM python:3.11-slim AS builder

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


FROM python:3.11-slim

LABEL maintainer="caio.mussatto@gmail.com"
LABEL version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000 \
    ENVIRONMENT=production \
    MPLCONFIGDIR=/tmp/matplotlib \
    NUMBA_CACHE_DIR=/tmp/numba_cache \
    HOME=/tmp

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN mkdir -p /app /data /logs \
    && chown -R appuser:appuser /app /data /logs

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY --chown=appuser:appuser \
    data/app.py \
    data/ui.py \
    data/server.py \
    data/functions.py \
    data/data.py \
    ./

COPY data/ ./data/
RUN ln -sf /data /app/data

USER appuser

CMD ["sh", "-c", "shiny run app.py --host 0.0.0.0 --port ${PORT}"]



