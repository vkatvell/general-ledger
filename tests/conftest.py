# tests/conftest.py

import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from app.db.models.ledger_entry_model import DBLedgerEntry
from app.schemas.ledger_entry_schema import LedgerEntryOut


@pytest.fixture
def async_mock_db():
    """Returns a fresh AsyncMock() DB session per test."""
    db = AsyncMock(spec=AsyncSession)
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.add = AsyncMock()
    return db


def make_mock_entry_out(
    entry: DBLedgerEntry,
    account_name: str,
    *,
    override_amount: Decimal | None = None,
    override_description: str | None = None,
    override_version: int | None = None,
    override_canadian_amount: Decimal | None = None,
) -> LedgerEntryOut:
    """
    Create a fully valid LedgerEntryOut object from a DBLedgerEntry instance,
    with optional overrides for amount, description, version, or CAD amount.
    """
    return LedgerEntryOut(
        id=entry.id,
        account_id=entry.account_id,
        idempotency_key=entry.idempotency_key,
        account_name=account_name,
        amount=override_amount if override_amount is not None else entry.amount,
        currency=entry.currency,
        description=(
            override_description
            if override_description is not None
            else entry.description
        ),
        date=entry.date,
        entry_type=entry.entry_type,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        version=override_version if override_version is not None else entry.version + 1,
        is_deleted=False,
        canadian_amount=(
            override_canadian_amount
            if override_canadian_amount is not None
            else Decimal("135.00")
        ),
    )


@pytest.fixture(autouse=True)
def patch_exchange_rate(monkeypatch):
    async def fake_rate():
        return 1.35

    monkeypatch.setattr("app.utils.currency.get_usd_to_cad_rate", fake_rate)
