- # Setup Guide for General Ledger Project
  
  This guide walks through how to run the General Ledger application locally using Docker Compose.  
  
---
- ## Prerequisites
- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [`uv` (for local Python workflows)](https://github.com/astral-sh/uv) *(optional)*
  
---
- ## 1. Clone the Repository
  
  ```
  git clone https://github.com/vkatvell/general-ledger.git
  cd general-ledger
  ```
  
---
- ## 2. Configure Environment Variables
  
  Copy the example file:  
  
  ```
  cp .env.example .env
  ```
  
  Edit the `.env` file with the correct values for:  
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- `DATABASE_URL`
- (Optional) `SENTRY_DSN`
  
---
- ## 3. Start the Application
  
  ```
  docker compose up --build
  ```
  
  Services:  
- Backend: [http://localhost:8000](http://localhost:8000)
- Frontend: [http://localhost:3000](http://localhost:3000)
- PostgreSQL: exposed on port 5434
  
---
- ## 4. Apply Migrations & Seed Data (Optional)
  
  To apply database migrations and seed initial data:  
  
  ```
  docker compose exec backend bash
  alembic upgrade head
  python scripts/seed_data.py
  ```
  
---
- ## 5. Run Tests (Optional)
  
  For local Python workflows outside Docker:  
  
  ```
  uv venv
  uv pip install -r requirements.txt
  pytest tests/
  ```
  
---
- ## 6. API Documentation
  
  Once the backend is running, visit:  
  
  ```
  http://localhost:8000/docs
  ```
  
  This provides interactive API docs using the OpenAPI spec.  
  
---
- ## Docker Compose Summary
  
  ```
  version: "3.8"
  
  services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    depends_on:
      - postgres
  
  frontend:
    build:
      context: ./frontend
      dockerfile: frontend.Dockerfile
    ports:
      - "3000:3000"
  
  postgres:
    image: postgres:15
    ports:
      - "5434:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  volumes:
  postgres_data:
  ```
  
---
