# Makefile - General Ledger Project

include .env
export

# Start FastAPI app with hot reload
dev:
	uvicorn app.main:app --reload

# Run pre-commit hooks
lint:
	pre-commit run --all-files

# Start/Stop Postgres via Docker
db-up:
	docker-compose up -d

db-down:
	docker-compose down

# Run Alembic migrations
migrate:
	alembic upgrade head

# Create new Alembic migration
migration:
	alembic revision --autogenerate -m "$(m)"

# Rebuild all DB schema (dev only!)
reset-db:
	alembic downgrade base
	rm alembic/versions/*.py
	alembic revision --autogenerate -m "Initial schema"
	alembic upgrade head

# Seed sample data
seed:
	PYTHONPATH=. uv run python scripts/seed.py

# Reset + reseed
seed-reset:
	PYTHONPATH=. uv run python scripts/seed.py --reset
