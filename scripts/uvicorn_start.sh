#!/usr/bin/env bash
set -euo pipefail
# Start the FastAPI app
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
