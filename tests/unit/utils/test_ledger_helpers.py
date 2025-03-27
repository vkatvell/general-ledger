import pytest
import uuid
from decimal import Decimal
from unittest.mock import patch
from datetime import datetime, timezone
from app.utils.ledger_helpers import inject_cad_amount, normalize_entry_type
from app.db.models.ledger_entry_model import DBLedgerEntry
from app.schemas.ledger_entry_schema import EntryType


@pytest.mark.asyncio
@patch("app.utils.ledger_helpers.get_usd_to_cad_rate", return_value=1.35)
async def test_inject_cad_amount(mock_rate):
    entry = DBLedgerEntry(
        id=uuid.uuid4(),
        account_id=uuid.uuid4(),
        idempotency_key=str(uuid.uuid4()),
        entry_type="debit",
        amount=Decimal("100.00"),
        currency="USD",
        description="Test",
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
    )

    result = await inject_cad_amount(entry)
    assert result.canadian_amount == Decimal("135.00")


def test_normalize_entry_type_enum():
    assert normalize_entry_type(EntryType.debit) == "debit"


def test_normalize_entry_type_string():
    assert normalize_entry_type("credit") == "credit"
