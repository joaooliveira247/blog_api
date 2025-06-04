FROM python:3.12-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY blog_api /app/blog_api
COPY pyproject.toml uv.lock main.py /app/

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache
