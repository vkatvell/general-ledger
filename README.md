# General Ledger Backend

A modular, testable backend system for managing a simple general ledger, designed with correctness, durability, and extensibility in mind.

---

## Features

- Full CRUD for ledger entries
- Soft deletes and versioning for all entries
- Dynamic currency conversion (USD → CAD) via U.S. Treasury API
- Summary endpoint for credit/debit aggregation and balance checks
- Account management (create, update, list active accounts)
- Basic test coverage with `pytest` and `unittest.mock`

---

## Tech Stack

- **Backend**: FastAPI (async)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Testing**: pytest + httpx + unittest.mock
- **Currency API**: U.S. Treasury Exchange Rate API

---

## Project Structure

```
app/
│
├── core/               # Settings, config, base classes
├── db/                 # SQLAlchemy models and DB setup
├── routes/             # FastAPI routes by resource
├── schemas/            # Pydantic input/output models
├── services/           # Business logic layer
├── utils/              # Shared helpers (e.g. DB queries, currency fetch)
└── main.py             # FastAPI app entrypoint
```

---

## Getting Started

### 1. Install Dependencies

This project uses [`uv`](https://github.com/astral-sh/uv) for managing virtual environments and dependencies.

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Update DB connection info and other settings as needed.

### 3. Apply Database Migrations

Ensure your PostgreSQL server is running and run:

```bash
alembic upgrade head
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

---

## Running Tests

```bash
pytest
```

This runs unit tests for entries, accounts, summary logic, and utility functions. All external API calls (e.g., exchange rate) are mocked.

---

## API Overview

| Method | Endpoint             | Description                           |
|--------|----------------------|---------------------------------------|
| POST   | `/api/entries/`      | Create a new ledger entry             |
| GET    | `/api/entries/`      | List entries (with filters)           |
| GET    | `/api/entries/{id}`  | Retrieve entry by ID                  |
| PATCH  | `/api/entries/{id}`  | Update entry amount or description    |
| DELETE | `/api/entries/{id}`  | Soft-delete a ledger entry            |
| GET    | `/api/summary/`      | Get debit/credit totals and balance   |
| POST   | `/api/accounts/`     | Create a new account                  |
| PATCH  | `/api/accounts/{id}` | Update account name or status         |
| GET    | `/api/accounts/`     | List all active accounts              |

---

## Development Notes

- Currency conversion uses the **latest daily Treasury rate** at response time. This is not persisted.
- Summaries are **computed on read** for consistency.
- All entries must be tied to an **active account**.
- Soft-deleted entries are excluded from summaries and queries.

---

## TODO / Future Enhancements

- [ ] Add structured logging
- [ ] Containerize with Docker
- [ ] Add background workers for audit logging or caching
- [ ] Build frontend dashboard (Next.js)

---

## License

MIT

