#!/usr/bin/env bash
set -e

alembic upgrade head
python3 scripts/import_football_events.py --dataset-dir data/premier_league_2025_26

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
