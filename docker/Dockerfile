FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app


FROM base AS builder

RUN pip install --no-cache-dir --upgrade pip poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.in-project true \
    && poetry install --without dev --no-root

COPY zigbee2mqtt_health /app/zigbee2mqtt_health/


FROM base AS runtime

COPY docker/*.sh /
COPY --from=builder /app /app

RUN mkdir -p /tmp /app \
    && chmod -R a+rX /app \
    && chmod -R a+rwX /tmp

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD /healthcheck.sh || exit 1

ENTRYPOINT ["/entrypoint.sh"]
