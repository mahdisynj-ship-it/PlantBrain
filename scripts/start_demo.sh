#!/usr/bin/env bash

set -e

echo "Running PlantBrain database migrations..."
alembic upgrade head

echo "Seeding PlantBrain demo data..."
python -m scripts.seed_demo_data

echo "Starting PlantBrain API..."
exec uvicorn app.api.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}"
  