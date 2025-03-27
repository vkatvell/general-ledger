# Dockerfile
FROM ghcr.io/astral-sh/uv:python3.11-alpine

# Set working directory
WORKDIR /app

# Optional: compile bytecode and set link mode
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Sync dependencies from lockfile (excluding dev dependencies)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Ensure .venv/bin is used as default path (no need to source)
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
