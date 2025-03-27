import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.ledger_entry_schema import LedgerEntryCreate, EntryType


def test_valid_ledger_entry_create():
    entry = LedgerEntryCreate(
        account_name="Cash",
        entry_type=EntryType.debit,
        amount=Decimal("100.00"),
        currency="USD",
        description="Valid entry",
        date=datetime.now(timezone.utc),
        idempotency_key=str(uuid.uuid4()),
    )
    assert entry.account_name == "Cash"
    assert entry.entry_type == EntryType.debit
    assert entry.amount == Decimal("100.00")
    assert entry.currency == "USD"


def test_invalid_entry_type():
    with pytest.raises(ValidationError) as exc:
        LedgerEntryCreate(
            account_name="Cash",
            entry_type="invalid",  # Not in Enum
            amount=Decimal("100.00"),
            currency="USD",
            description="Invalid type",
            date=datetime.now(timezone.utc),
            idempotency_key=uuid.uuid4(),
        )
    assert "entry_type" in str(exc.value)


def test_negative_amount():
    with pytest.raises(ValidationError) as exc:
        LedgerEntryCreate(
            account_name="Cash",
            entry_type=EntryType.credit,
            amount=Decimal("-20.00"),  # Invalid negative
            currency="USD",
            description="Invalid amount",
            date=datetime.now(timezone.utc),
            idempotency_key=uuid.uuid4(),
        )
    assert "amount" in str(exc.value)


def test_currency_too_short():
    with pytest.raises(ValidationError) as exc:
        LedgerEntryCreate(
            account_name="Cash",
            entry_type=EntryType.debit,
            amount=Decimal("10.00"),
            currency="US",  # Too short
            description=None,
            date=datetime.now(timezone.utc),
            idempotency_key=uuid.uuid4(),
        )
    assert "currency" in str(exc.value)


def test_currency_too_long():
    with pytest.raises(ValidationError) as exc:
        LedgerEntryCreate(
            account_name="Cash",
            entry_type=EntryType.credit,
            amount=Decimal("50.00"),
            currency="USDX",  # Too long
            description=None,
            date=datetime.now(timezone.utc),
            idempotency_key=uuid.uuid4(),
        )
    assert "currency" in str(exc.value)


def test_missing_idempotency_key():
    with pytest.raises(ValidationError) as exc:
        LedgerEntryCreate(
            account_name="Cash",
            entry_type=EntryType.debit,
            amount=Decimal("10.00"),
            currency="USD",
            description="No key",
            date=datetime.now(timezone.utc),
            # idempotency_key is missing
        )
    assert "idempotency_key" in str(exc.value)
