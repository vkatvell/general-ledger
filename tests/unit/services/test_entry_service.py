import pytest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
from app.schemas.ledger_entry_schema import LedgerEntryCreate, EntryType, LedgerEntryOut
from app.services.entry_service import create_entry
from app.db.models import DBAccount, DBLedgerEntry


@pytest.mark.asyncio
async def test_create_entry_success(async_mock_db):
    entry = LedgerEntryCreate(
        account_name="Cash",
        entry_type=EntryType.debit,
        amount=Decimal("100.00"),
        currency="USD",
        description="Initial deposit",
        date=datetime.now(timezone.utc),
        idempotency_key=uuid.uuid4(),
    )

    # Setup account lookup
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)
    account_result = MagicMock()
    account_result.scalar_one_or_none = AsyncMock(return_value=account)

    # Setup idempotency check = no duplicate
    idempotency_result = MagicMock()
    idempotency_result.scalar_one_or_none = AsyncMock(return_value=None)

    async_mock_db.execute = AsyncMock(side_effect=[account_result, idempotency_result])

    # Patch DB add to fully populate new entry for Pydantic validation
    async_mock_db.add = AsyncMock()

    async def fake_refresh(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)
        obj.version = 1
        obj.is_deleted = False
        obj.account = account
        obj.account_id = account.id
        return obj

    async_mock_db.refresh.side_effect = fake_refresh
    async_mock_db.commit = AsyncMock()

    result = await create_entry(entry, async_mock_db)

    assert isinstance(result, LedgerEntryOut)
    assert result.amount == entry.amount
    assert result.account_name == "Cash"


@pytest.mark.asyncio
async def test_create_entry_account_missing(async_mock_db):
    entry = LedgerEntryCreate(
        account_name="Unknown",
        entry_type=EntryType.credit,
        amount=Decimal("50.00"),
        currency="USD",
        description="Ghost account",
        date=datetime.now(timezone.utc),
        idempotency_key=uuid.uuid4(),
    )

    result = MagicMock()
    result.scalar_one_or_none = AsyncMock(return_value=None)
    async_mock_db.execute = AsyncMock(return_value=result)

    with pytest.raises(HTTPException) as exc:
        await create_entry(entry, async_mock_db)

    assert exc.value.status_code == 404
    assert "Account not found" in exc.value.detail


@pytest.mark.asyncio
async def test_create_entry_idempotent_conflict(async_mock_db):
    key = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    entry = LedgerEntryCreate(
        account_name="Cash",
        entry_type=EntryType.debit,
        amount=Decimal("999.99"),
        currency="USD",
        description="Conflict entry",
        date=datetime.now(timezone.utc),
        idempotency_key=key,
    )

    # Matching account
    account_result = MagicMock()
    account_result.scalar_one_or_none = AsyncMock(return_value=account)

    # Existing entry with same key but different amount
    existing = DBLedgerEntry(
        id=uuid.uuid4(),
        account_id=account.id,
        entry_type=EntryType.debit,
        amount=Decimal("10.00"),
        currency="USD",
        description="Old entry",
        idempotency_key=key,
        date=entry.date,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )
    existing_result = MagicMock()
    existing_result.scalar_one_or_none = AsyncMock(return_value=existing)

    async_mock_db.execute = AsyncMock(side_effect=[account_result, existing_result])

    with pytest.raises(HTTPException) as exc:
        await create_entry(entry, async_mock_db)

    assert exc.value.status_code == 409
    assert "Idempotency key already used" in exc.value.detail
