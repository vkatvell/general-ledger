# General Ledger – Take-Home Assignment
  
  **Author:** Venkat Vellanki  
  
  A containerized general ledger system built with FastAPI and Next.js. The project supports creating, updating, and summarizing ledger entries and accounts, with PostgreSQL as the database and Docker Compose for local development.  

## Tech Stack
- **Backend**: FastAPI, async SQLAlchemy, Alembic
- **Frontend**: Next.js, TailwindCSS, ShadCN UI
- **Database**: PostgreSQL (via Docker)
- **Dev Tools**: Docker Compose, `uv`, pytest

## Getting Started
  
  To run the project locally using Docker Compose, follow the full setup guide in [docs/setup.md](./docs/setup.md). 

## Project Structure
  
  ```
  .
  ├── alembic/              # Database migrations
  ├── app/                  # FastAPI backend application
  ├── frontend/             # Next.js frontend app
  ├── scripts/              # Seed scripts and utility helpers
  ├── tests/                # Unit and integration test suite
  ├── docs/                 # Project documentation
  ├── docker-compose.yml    # Docker Compose configuration
  ├── Dockerfile            # Backend Dockerfile
  ├── frontend.Dockerfile   # Frontend Dockerfile (inside ./frontend)
  ├── .env.example          # Environment variable template
  ├── Makefile              # Development convenience commands
  └── README.md             # Project overview
  ```

## API Documentation
  
  Once running, visit:  
  
  ```
  http://localhost:8000/docs
  ```
  
  This serves the OpenAPI specification for the backend.
