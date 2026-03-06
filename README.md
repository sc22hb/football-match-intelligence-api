# Football Match Intelligence API

Data-driven football analytics API built with FastAPI, SQLAlchemy, and PostgreSQL for COMP3011 coursework.

## Current Status

- Phase 0 to Phase 5 complete (foundation, CRUD models, analytics endpoints, tests)
- Phase 6 in progress (dataset import pipeline and documentation)

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic
- Pytest
- PostgreSQL

## Architecture

- API Routes -> Services -> Repositories -> Database
- Analytics calculations implemented under `app/analytics/`

## Quick Start (Local PostgreSQL)

1. Configure environment

```bash
cp .env.example .env
```

2. Install dependencies

```bash
python3 -m pip install -e .
```

3. Apply migrations

```bash
python3 -m alembic upgrade head
```

4. Run API

```bash
uvicorn app.main:app --reload
```

OpenAPI docs:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Running Tests

```bash
python3 -m pytest -q
```

## Implemented Endpoints

Health

- `GET /health`

Teams CRUD

- `POST /teams`
- `GET /teams`
- `GET /teams/{team_id}`
- `PUT /teams/{team_id}`
- `DELETE /teams/{team_id}`

Players CRUD

- `POST /players`
- `GET /players`
- `GET /players/{player_id}`
- `PUT /players/{player_id}`
- `DELETE /players/{player_id}`

Matches CRUD

- `POST /matches`
- `GET /matches`
- `GET /matches/{match_id}`
- `PUT /matches/{match_id}`
- `DELETE /matches/{match_id}`

Events

- `POST /events`
- `GET /events`

Analytics

- `GET /analytics/team-form/{team_id}`
- `GET /analytics/league-table`
- `GET /analytics/top-scorers`

## Dataset Integration

Target dataset:

- Football Events Dataset (Kaggle) by `secareanualin`

The full dataset is not committed. A reproducible sample is available in `data/sample/`.

Import command (sample):

```bash
python3 scripts/import_football_events.py --dataset-dir data/sample
```

Useful options:

- `--dry-run` to validate input without persisting
- `--database-url` to target a specific DB

## Dataset Documentation

- `docs/dataset_exploration.md`
- `docs/ai_dataset_worklog.txt`

## Coursework Roadmap

- Phase 6: dataset import + citation docs + smoke test
- Phase 7: advanced analytics (team strength, explainable form, player impact)
- Phase 8: research/report documentation and final polish
