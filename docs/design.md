# Design Document – General Ledger System
## Overview
  
  This document outlines the architecture, design decisions, and implementation strategy for a general ledger backend system built with **FastAPI**, **PostgreSQL**, and **async SQLAlchemy**. The system emphasizes **correctness**, **durability**, and **modularity**, with a focus on extensibility and testability.  
  
---
## 1. Architecture Summary
- **Backend Framework**: FastAPI (async)
- **Logging & Monitoring**: Structured logging with optional Sentry integration
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (async)
- **Validation**: Pydantic
- **Migrations**: Alembic
- **Testing**: pytest
- **Currency Conversion**: U.S. Treasury Exchange Rate API (via httpx)
### Key Modules
- `services/`: Business logic for entries, accounts, summaries
- `utils/`: Shared helpers (e.g., currency conversion, validation)
- `schemas/`: Pydantic I/O schemas
- `routes/`: Resource-based API routing
  
---
## 2. Core Features
- ### Ledger Entries
- CRUD operations with idempotency guarantees
- Linked to active accounts
- Supports `debit` or `credit` types, versioning, and soft deletion
- Optional filters: account_name, currency, start_date, end_date
- ### Accounts
- UUID-based primary keys
- Unique name constraint
- Active/inactive status without deletion
- ### Summarization
- `/summary` endpoint provides count and total of debits and credits
- Includes `is_balanced` check
- ### Currency Conversion
- `canadian_amount` computed at read-time using live exchange rates
- Conversion logic isolated to `utils/currency.py`
  
---
## 3. Key Design Trade-offs & Justifications
  
  | Decision | Rationale |
  |---|---|
  | **UUIDs for IDs** | Ensures global uniqueness and safety for future horizontal scaling or multi-tenant environments. UUIDs also decouple ID generation from database sequences, allowing clients or services to generate IDs independently. |
  | **Soft deletes** | Preserves historical record integrity and supports auditability. Soft deletion avoids the irreversible loss of financial data, which is essential for traceability, compliance, and potential restoration workflows. |
  | **Entry versioning** | A version field is incremented with each update, allowing the system to track changes over time and support rudimentary audit trails without a full audit log. This helps resolve disputes or validate historical states. |
  | **Compute-on-read summaries** | Summary statistics (e.g., total debits/credits) are computed live at query time to prevent data drift and ensure consistency. This avoids the complexity of keeping denormalized aggregates in sync. Acceptable for current data volumes; performance can be optimized later via materialized views or caching. |
  | **Async DB sessions** | Using async SQLAlchemy sessions improves performance under concurrent request load. Async is especially beneficial in I/O-bound workloads like database and API access, ensuring scalability of the backend. |
  | **Live currency conversion** | Using the U.S. Treasury exchange rate API at read-time avoids stale values without the need to store historical rates. This simplifies implementation and ensures consistency, though future support for historical rates is considered. |
  | **Strict idempotency with UUID keys** | POST requests require a client-supplied idempotency_key (UUID format). This prevents accidental duplicate entry creation during retries and provides a consistent, stateless way to enforce request safety. Conflicts are returned if reused with differing data. |
- ### Entries
  - Entries are strictly linked to active accounts via foreign key constraints to ensure referential integrity.
  - Each entry must have a positive amount, while its financial intent (addition or subtraction) is determined by entry_type (debit or credit).
  - Updates are restricted to mutable fields (amount, description) to preserve the original semantics of the transaction.
  - A version field and updated_at timestamp are updated with each modification, enabling historical tracking without requiring a full audit log.
  - Entries are soft-deleted via the is_deleted flag, ensuring that no financial data is permanently lost while allowing logical deletion from active queries.
  - Query filters for account_name, currency, and date ranges are supported to enable precise financial inspection via the API.
- ### Accounts
  - Each account is identified by a UUID and has a unique name enforced at the database level.
  - Accounts can be toggled active or inactive without deletion, enabling long-term historical recordkeeping.
  - The is_active flag controls whether an account can be used for new entries or viewed in the listing of all accounts.
- ### Summary
  - The /summary endpoint aggregates debit and credit counts and totals in real time using efficient SQL queries.
  - This ensures accuracy without relying on redundant storage or background sync processes.
  - Optional filters allow scoped inspection by account, currency, or time range.
  - The current implementation performs well at modest scale; materialized views or Redis caching are viable paths for optimization.
- ### Idempotency Trade-offs
  - The backend enforces a required client-supplied idempotency_key for all POST /entries requests.
  - Keys must be UUID strings, which are highly collision-resistant and suitable for stateless clients retrying failed submissions.
  - If the same key is submitted with identical data, the original result is returned — avoiding duplicate entries.
  - If the same key is submitted with different data, a 409 Conflict is returned to preserve consistency.
  - This approach eliminates the need for complex client/server coordination and supports robust retry semantics.
  - UUID-based keys are more verbose than sequential tokens, but provide greater safety and align with distributed design principles.
---
- ## 4. UI Overview
  
  A minimalist **Next.js** frontend is provided to:  
  - Create, read, update, and delete entries
  - View accounts
  - Track ledger balance status via `/summary` API endpoint
  
  UI is built with:  
  - TailwindCSS + ShadCN components
  - REST API integration
  - Dockerized for local dev alongside backend
  
---
## 5. Docker & Local Dev
  - All services (backend, frontend, PostgreSQL) run in containers
  - Docker Compose handles orchestration
  - `.env` for shared configuration across services
  - `alembic` used for migration management
  - Frontend: [http://localhost:3000](http://localhost:3000)
  - Backend: [http://localhost:8000](http://localhost:8000)
  - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
  
---
## 6. Testing & Validation
- **Unit Tests**: CRUD operations, summary logic, conversion helpers
- **Validation**:
	- Pydantic schemas for strict input enforcement
	- Business rule checks in service layer
- **Mocks**: Currency API mocked in tests
  
---
## 7. Extensibility & Future Work
- Double-entry transaction support (via grouped entries)
- Audit log table for immutable change tracking
- Redis caching for expensive summary queries
- Authentication and user-scoped ledger visibility
- Historical exchange rate support for backdated summaries