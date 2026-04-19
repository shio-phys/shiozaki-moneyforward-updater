FROM python:3.14-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

RUN uv run playwright install chromium --with-deps

COPY main.py ./

ENTRYPOINT ["uv", "run", "python", "main.py"]
