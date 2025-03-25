import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.services.summary_service import get_summary
from app.schemas.ledger_entry_schema import EntryType
from app.schemas.summary_schema import SummaryOut


@pytest.mark.asyncio
async def test_get_summary_returns_zero_when_no_entries(async_mock_db):
    # Simulate no account match (if account_name is given), and no entries
    mock_result = MagicMock()
    mock_result.all = MagicMock(return_value=[])
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_summary(async_mock_db)

    assert result == SummaryOut(
        num_debits=0,
        total_debit_amount=Decimal("0.00"),
        num_credits=0,
        total_credit_amount=Decimal("0.00"),
        is_balanced=True,
    )


@pytest.mark.asyncio
async def test_get_summary_balanced(async_mock_db):
    # Simulate account lookup
    mock_result = MagicMock()
    mock_result.all = MagicMock(
        return_value=[
            (EntryType.debit, 2, Decimal("6000.00")),
            (EntryType.credit, 2, Decimal("6000.00")),
        ]
    )
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 2
    assert result.total_debit_amount == Decimal("6000.00")
    assert result.num_credits == 2
    assert result.total_credit_amount == Decimal("6000.00")
    assert result.is_balanced is True


@pytest.mark.asyncio
async def test_get_summary_unbalanced(async_mock_db):
    # No account_name filter this time
    mock_result = MagicMock()
    mock_result.all = MagicMock(
        return_value=[
            (EntryType.debit, 1, Decimal("150.00")),
            (EntryType.credit, 1, Decimal("100.00")),
        ]
    )
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 1
    assert result.total_debit_amount == Decimal("150.00")
    assert result.num_credits == 1
    assert result.total_credit_amount == Decimal("100.00")
    assert result.is_balanced is False


@pytest.mark.asyncio
async def test_get_summary_ignores_soft_deleted(async_mock_db):
    entries_result = MagicMock()
    entries_result.all = MagicMock(return_value=[])
    async_mock_db.execute = AsyncMock(return_value=entries_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 0
    assert result.total_credit_amount == Decimal("0.00")
    assert result.is_balanced is True


@pytest.mark.asyncio
async def test_get_summary_with_only_debits(async_mock_db):
    # Simulate a query that returns only debit entries
    mock_result = MagicMock()
    mock_result.all = MagicMock(
        return_value=[
            (EntryType.debit, 3, Decimal("450.00")),
        ]
    )
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 3
    assert result.total_debit_amount == Decimal("450.00")
    assert result.num_credits == 0
    assert result.total_credit_amount == Decimal("0.00")
    assert result.is_balanced is False


@pytest.mark.asyncio
async def test_get_summary_with_only_credits(async_mock_db):
    # Simulate a query that returns only credit entries
    mock_result = MagicMock()
    mock_result.all = MagicMock(
        return_value=[
            (EntryType.credit, 2, Decimal("300.00")),
        ]
    )
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    result = await get_summary(async_mock_db)

    assert isinstance(result, SummaryOut)
    assert result.num_debits == 0
    assert result.total_debit_amount == Decimal("0.00")
    assert result.num_credits == 2
    assert result.total_credit_amount == Decimal("300.00")
    assert result.is_balanced is False
