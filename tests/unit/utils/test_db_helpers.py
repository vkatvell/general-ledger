import pytest
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils import db_helpers
from app.db.models import DBAccount, DBLedgerEntry


@pytest.mark.asyncio
async def test_get_entry_or_raise_404_found():
    entry = DBLedgerEntry(id=uuid.uuid4(), is_deleted=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = entry
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = mock_result

    result = await db_helpers.get_entry_or_raise_404(str(entry.id), db)
    assert result == entry


@pytest.mark.asyncio
async def test_get_entry_or_raise_404_not_found():
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with pytest.raises(HTTPException) as exc:
        await db_helpers.get_entry_or_raise_404("nonexistent", db)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_debit_credit_totals():
    db = AsyncMock(spec=AsyncSession)
    expected = [("debit", 2, Decimal("100.00"))]

    mock_result = MagicMock()
    mock_result.all.return_value = expected
    db.execute.return_value = mock_result

    result = await db_helpers.get_debit_credit_totals(db)
    assert result == expected


@pytest.mark.asyncio
async def test_get_account_or_raise_404_found():
    account = DBAccount(id=uuid.uuid4(), name="Cash")
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=account)
    )

    result = await db_helpers.get_account_or_raise_404(account.id, db)
    assert result == account


@pytest.mark.asyncio
async def test_get_account_or_raise_404_not_found():
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with pytest.raises(HTTPException):
        await db_helpers.get_account_or_raise_404(uuid.uuid4(), db)


@pytest.mark.asyncio
async def test_account_name_exists_true():
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=DBAccount())
    )

    assert await db_helpers.account_name_exists("Cash", db) is True


@pytest.mark.asyncio
async def test_account_name_exists_false():
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    assert await db_helpers.account_name_exists("Ghost", db) is False


@pytest.mark.asyncio
async def test_get_active_account_by_name_found():
    account = DBAccount(name="Active", is_active=True)
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=account)
    )

    result = await db_helpers.get_active_account_by_name("Active", db)
    assert result == account


@pytest.mark.asyncio
async def test_get_active_account_by_name_not_found():
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(scalar_one_or_none=MagicMock(return_value=None))

    with pytest.raises(HTTPException):
        await db_helpers.get_active_account_by_name("Inactive", db)


@pytest.mark.asyncio
async def test_get_account_by_name_returns_account():
    account = DBAccount(name="Cash")
    db = AsyncMock(spec=AsyncSession)
    db.execute.return_value = MagicMock(
        scalar_one_or_none=MagicMock(return_value=account)
    )

    result = await db_helpers.get_account_by_name("Cash", db)
    assert result == account
