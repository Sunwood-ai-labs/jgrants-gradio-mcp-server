# syntax=docker/dockerfile:1

# Build stage using official uv image
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy application code
COPY jgrants_mcp_server ./jgrants_mcp_server

# Runtime stage
FROM python:3.11-slim-bookworm

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/jgrants_mcp_server ./jgrants_mcp_server
COPY --from=builder /app/pyproject.toml ./
COPY --from=builder /app/README.md ./

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    JGRANTS_FILES_DIR=/app/jgrants_files

# Create directory for downloaded files
RUN mkdir -p ${JGRANTS_FILES_DIR}

# Expose port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:7860/').raise_for_status()" || exit 1

# Run the application
CMD ["python", "-m", "jgrants_mcp_server", "--host", "0.0.0.0", "--port", "7860"]
