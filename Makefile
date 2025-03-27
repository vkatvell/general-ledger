# Makefile - General Ledger Project

include .env
export

# Start FastAPI app with hot reload and Next.js UI
dev-backend:
	@echo "Starting backend..."
	(uvicorn app.main:app --reload)

# Start Next.js UI app
dev-frontend:
	@echo "Starting frontend..."
	(cd frontend/general-ledger-ui && npm run dev)
# Run pre-commit hooks
lint:
	pre-commit run --all-files

# Run unit tests
test:
	uv run pytest tests

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
	ifndef m
		$(error You must specify a message: make migration m="Add new table")
	endif
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
