FROM python:3.14-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app


FROM base AS builder

RUN pip install --no-cache-dir --upgrade pip poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.in-project true \
    && poetry install --without dev --no-root

COPY src /app/src

RUN poetry install --without dev


FROM base AS runtime

COPY --from=builder /app /app

RUN mkdir -p /tmp /app \
    && chmod -R a+rX /app \
    && chmod -R a+rwX /tmp

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -m zigbee2mqtt_health.liveness || exit 1

ENTRYPOINT [python, -m, zigbee2mqtt_health.main]
