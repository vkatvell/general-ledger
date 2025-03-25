# tests/conftest.py

import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def async_mock_db():
    """Returns a fresh AsyncMock() DB session per test."""
    db = AsyncMock(spec=AsyncSession)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.add = AsyncMock()
    return db
