FROM python:3.11-alpine

WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apk add --no-cache curl

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies (no cache to keep image small)
RUN uv sync --no-dev --no-cache

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
