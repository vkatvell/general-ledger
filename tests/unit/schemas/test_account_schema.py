import pytest
import uuid
from datetime import datetime, timezone
from pydantic import ValidationError

from app.schemas.account_schema import (
    AccountCreate,
    AccountUpdate,
    AccountOut,
)


def test_valid_account_create():
    account = AccountCreate(name="Cash", is_active=True)
    assert account.name == "Cash"
    assert account.is_active is True


def test_valid_account_create_default_active():
    account = AccountCreate(name="Savings")
    assert account.name == "Savings"
    assert account.is_active is True  # default


def test_account_create_missing_name():
    with pytest.raises(ValidationError) as exc:
        AccountCreate(is_active=True)  # name is required
    assert "name" in str(exc.value)


def test_account_update_partial_name_only():
    update = AccountUpdate(name="Revenue")
    assert update.name == "Revenue"
    assert update.is_active is None


def test_account_update_partial_is_active_only():
    update = AccountUpdate(is_active=False)
    assert update.name is None
    assert update.is_active is False


def test_account_out_success():
    out = AccountOut(
        id=uuid.uuid4(),
        name="Assets",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    assert out.name == "Assets"
    assert isinstance(out.id, uuid.UUID)
    assert isinstance(out.created_at, datetime)
