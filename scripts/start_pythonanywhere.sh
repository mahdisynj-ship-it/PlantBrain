#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

export PLANTBRAIN_DEMO_MODE="${PLANTBRAIN_DEMO_MODE:-true}"
export PLANTBRAIN_FRONTEND_ORIGIN="${PLANTBRAIN_FRONTEND_ORIGIN:-https://mahdisynj-ship-it.github.io}"
export PLANTBRAIN_DATABASE_URL="${PLANTBRAIN_DATABASE_URL:-sqlite:///${PROJECT_DIR}/data/database/plantbrain.db}"

if [ -z "${DOMAIN_SOCKET:-}" ]; then
    echo "DOMAIN_SOCKET is required for the PythonAnywhere ASGI deployment."
    exit 1
fi

cd "${PROJECT_DIR}"

mkdir -p data/database

echo "Running PlantBrain database migrations..."
"${VENV_DIR}/bin/alembic" upgrade head

echo "Seeding PlantBrain demo data..."
"${VENV_DIR}/bin/python" -m scripts.seed_demo_data

echo "Starting PlantBrain API..."
exec "${VENV_DIR}/bin/uvicorn" \
    --app-dir "${PROJECT_DIR}" \
    --uds "${DOMAIN_SOCKET}" \
    app.api.main:app
    