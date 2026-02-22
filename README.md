# Financial Consolidation Engine

## Important notice

This repository is an educational/demo project. It was implemented in a few hours as a technical exercise and may contain bugs, shortcuts, and architectural decisions that have not been carefully weighed. Do not use this project in production or as a definitive reference for production systems.

## What this application does

- Provides a minimal financial consolidation engine (basic P&L generation) and a small HTTP API to exercise it.
- Supports importing transactions from CSV files into a local PostgreSQL database and generating P&L reports from either imported or sample data.

## Project structure and useful artifacts

- Main source code: `app/` (endpoints, domain models, infrastructure, connectors).
- CSV connector: `app/infrastructure/connectors/csv_connector.py` — validates required columns (`date`, `account_id`, `amount`) and normalizes rows.
- CSV import endpoint: `POST /api/v1/data-sources/csv/import` (handler in `app/api/v1/endpoints/data_sources.py`).
- Example CSV included: `sample_csvs/test_transactions.csv`.

## Requirements

- Docker + docker-compose (recommended) or Python 3.11+ with access to a PostgreSQL instance.
- Optional: create and activate a virtual environment and install dependencies listed in `pyproject.toml`.

## Quick start (Docker)

1. Start services:

```bash
docker-compose up --build -d
```

2. (Optional) Seed sample data inside the `web` container:

```bash
docker-compose exec web python scripts/seed_data.py
```

3. Open the API docs: http://localhost:8000/docs

## Importing the example CSV

Use the provided example CSV at `sample_csvs/test_transactions.csv` to exercise the CSV import endpoint.

## Expected response

The API returns JSON including at least `success_count` and `error_count` (rows parsed successfully vs parse errors) and `persisted_count` indicating how many rows were stored in the database. It also returns lists with partial errors: `parsed_errors` and `persist_errors`.

## Running locally without Docker

1. Create a virtual environment and install dependencies (see `pyproject.toml`).
2. Set `DATABASE_URL` to point at your Postgres instance (e.g. `postgresql+asyncpg://postgres:postgres@localhost:5432/fce`).
3. Start the app:

```bash
.venv\Scripts\Activate.ps1  # Windows PowerShell
uvicorn app.main:app --reload
```

## Tests and code quality

- Run tests (unit + integration):

```bash
.venv\Scripts\pytest -q
```

- The project uses `ruff` for linting; run:

```bash
.venv\Scripts\python -m ruff check .
```

## License and use

This repository is provided for educational purposes only. There is no warranty; the author is not responsible for any misuse.

**_ End of README _**
