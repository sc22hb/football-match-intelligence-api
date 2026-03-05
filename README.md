# Football Match Intelligence API

Data-driven football analytics API built with FastAPI, SQLAlchemy, and PostgreSQL for COMP3011 coursework.

## Current Status

- `Phase 0` complete: foundation + health check + SQLAlchemy config + pytest scaffold
- `Phase 1` in progress: Team model, migration, CRUD API, and tests

## Project Overview

The project provides football data management and analytics endpoints with a layered architecture:

- API routes (HTTP layer)
- Services (business logic)
- Repositories (database access only)
- Database (PostgreSQL + Alembic migrations)

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy 2.0
- Alembic
- Pydantic
- Pytest
- PostgreSQL

## Quick Start (Local PostgreSQL)

### 1) Prerequisites

- Python 3.11
- PostgreSQL 16 (running locally)

### 2) Configure environment

```bash
cp .env.example .env
```

### 3) Install dependencies

```bash
python3 -m pip install -e .
```

### 4) Apply database migrations

```bash
python3 -m alembic upgrade head
```

### 5) Run the API

```bash
uvicorn app.main:app --reload
```

API docs are available at:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Running Tests

```bash
python3 -m pytest -q
```

## Implemented Endpoints (Current)

- `GET /health`
- `POST /teams`
- `GET /teams`
- `GET /teams/{team_id}`
- `PUT /teams/{team_id}`
- `DELETE /teams/{team_id}`

## Coursework Roadmap

- Phase 2: Players
- Phase 3: Matches
- Phase 4: Events
- Phase 5: Basic analytics
- Phase 6: Kaggle dataset import
- Phase 7: Advanced analytics
- Phase 8: Documentation polish + report notes

## Dataset Plan

Target dataset for integration:

- Football Events Dataset by `secareanualin` (Kaggle)

Citation details and import notes will be added in `docs/dataset_exploration.md` and `docs/research_notes.md`.
