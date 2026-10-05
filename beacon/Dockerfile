FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# Install dependencies first so they're cached across source changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev

RUN useradd --system --no-create-home beacon
USER beacon

# Runtime-only files are mounted by docker-compose, not baked into the image:
#   /app/src/beacon/data/GeoLite2-City.mmdb, /app/data_sources.yaml, /app/migrations
EXPOSE 8000
CMD ["uvicorn", "beacon.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
