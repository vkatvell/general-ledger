import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from app.services.summary_service import get_summary
from app.schemas.ledger_entry_schema import EntryType
from app.schemas.summary_schema import SummaryOut
from app.db.models import DBAccount


@pytest.mark.asyncio
async def test_get_summary_returns_zero_when_no_entries(async_mock_db):
    # Simulate no account match (if account_name is given), and no entries
    account_result = MagicMock()
    account_result.first = AsyncMock(return_value=None)

    entries_result = MagicMock()
    entries_result.all = AsyncMock(return_value=[])

    async_mock_db.execute = AsyncMock(side_effect=[account_result, entries_result])

    result = await get_summary(async_mock_db, account_name="Nonexistent")

    assert result == SummaryOut(
        num_debits=0,
        total_debit_amount=Decimal("0.00"),
        num_credits=0,
        total_credit_amount=Decimal("0.00"),
        is_balanced=True,
    )


@pytest.mark.asyncio
async def test_get_summary_balanced_debits_and_credits(async_mock_db):
    # Simulate account lookup
    account_id = uuid.uuid4()
    account_result = MagicMock()
    account_result.first = AsyncMock(return_value=[account_id])

    # Simulate grouped debit and credit entries
    entries_result = MagicMock()
    entries_result.all = AsyncMock(
        return_value=[
            (EntryType.debit, 2, Decimal("200.00")),
            (EntryType.credit, 2, Decimal("200.00")),
        ]
    )

    async_mock_db.execute = AsyncMock(side_effect=[account_result, entries_result])

    result = await get_summary(async_mock_db, account_name="Cash")

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 2
    assert result.total_debit_amount == Decimal("200.00")
    assert result.num_credits == 2
    assert result.total_credit_amount == Decimal("200.00")
    assert result.is_balanced is True


@pytest.mark.asyncio
async def test_get_summary_unbalanced(async_mock_db):
    # No account_name filter this time
    entries_result = MagicMock()
    entries_result.all = AsyncMock(
        return_value=[
            (EntryType.debit, 1, Decimal("120.00")),
            (EntryType.credit, 1, Decimal("50.00")),
        ]
    )

    async_mock_db.execute = AsyncMock(return_value=entries_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 1
    assert result.total_debit_amount == Decimal("120.00")
    assert result.num_credits == 1
    assert result.total_credit_amount == Decimal("50.00")
    assert result.is_balanced is False


@pytest.mark.asyncio
async def test_get_summary_filters_currency_and_dates(async_mock_db):
    # Mock all() return with only debit rows
    entries_result = MagicMock()
    entries_result.all = AsyncMock(
        return_value=[
            (EntryType.debit, 3, Decimal("75.00")),
        ]
    )

    async_mock_db.execute = AsyncMock(return_value=entries_result)

    result = await get_summary(
        db=async_mock_db,
        currency="eur",
        start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2024, 12, 31, tzinfo=timezone.utc),
    )

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 3
    assert result.total_debit_amount == Decimal("75.00")
    assert result.num_credits == 0
    assert result.total_credit_amount == Decimal("0.00")
    assert result.is_balanced is False


@pytest.mark.asyncio
async def test_get_summary_ignores_soft_deleted(async_mock_db):
    entries_result = MagicMock()
    entries_result.all = AsyncMock(return_value=[])  # Simulate no results returned

    async_mock_db.execute = AsyncMock(return_value=entries_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 0
    assert result.num_credits == 0


@pytest.mark.asyncio
async def test_get_summary_skips_inactive_account(async_mock_db):
    account_result = MagicMock()
    account_result.first = AsyncMock(
        return_value=None
    )  # Simulate no match due to inactive account

    entries_result = MagicMock()
    entries_result.all = AsyncMock(return_value=[])

    async_mock_db.execute = AsyncMock(side_effect=[account_result, entries_result])

    result = await get_summary(async_mock_db, account_name="InactiveAccount")

    assert isinstance(result, SummaryOut)
    assert result.total_credit_amount == Decimal("0.00")
    assert result.num_debits == 0
    assert result.is_balanced is True


@pytest.mark.asyncio
async def test_get_summary_with_only_debits(async_mock_db):
    # Simulate a query that returns only debit entries
    entries_result = MagicMock()
    entries_result.all = AsyncMock(
        return_value=[(EntryType.debit, 3, Decimal("150.00"))]
    )

    async_mock_db.execute = AsyncMock(return_value=entries_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 3
    assert result.total_debit_amount == Decimal("150.00")
    assert result.num_credits == 0
    assert result.total_credit_amount == Decimal("0.00")
    assert result.is_balanced is False


@pytest.mark.asyncio
async def test_get_summary_with_only_credits(async_mock_db):
    # Simulate a query that returns only credit entries
    entries_result = MagicMock()
    entries_result.all = AsyncMock(
        return_value=[
            (EntryType.credit, 4, Decimal("400.00")),
        ]
    )

    async_mock_db.execute = AsyncMock(return_value=entries_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 0
    assert result.total_debit_amount == Decimal("0.00")
    assert result.num_credits == 4
    assert result.total_credit_amount == Decimal("400.00")
    assert result.is_balanced is False
