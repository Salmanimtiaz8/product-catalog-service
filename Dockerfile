# multi-stage build for smaller images
FROM python:3.11-slim AS base

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /srv

# Leverage pip cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY app ./app
COPY scripts/uvicorn_start.sh ./uvicorn_start.sh
RUN chmod +x ./uvicorn_start.sh

EXPOSE 8000

# Healthcheck hitting /health
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8000/health || exit 1

ENV PORT=8000
ENV DATABASE_URL=sqlite:///./app.db

CMD ["./uvicorn_start.sh"]
