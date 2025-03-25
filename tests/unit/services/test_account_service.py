import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
from app.schemas.account_schema import (
    AccountCreate,
    AccountOut,
    AccountListResponse,
    AccountUpdate,
)
from app.services.account_service import create_account, update_account
from app.db.models import DBAccount


@pytest.mark.asyncio
async def test_create_account_success(async_mock_db):
    account_data = AccountCreate(name="Legal Fees")
    mock_account = DBAccount(
        id=uuid.uuid4(),
        name="Legal Fees",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    # Mock account existence check to return no existing account
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    async_mock_db.add = AsyncMock()
    async_mock_db.commit = AsyncMock()
    async_mock_db.refresh = AsyncMock()

    async_mock_db.refresh.side_effect = lambda obj: obj.__dict__.update(
        {
            "id": mock_account.id,
            "is_active": True,
            "created_at": mock_account.created_at,
        }
    )

    result = await create_account(account_data, async_mock_db)

    assert isinstance(result, AccountOut)
    assert result.name == "Legal Fees"
    assert result.is_active is True


@pytest.mark.asyncio
async def test_create_account_duplicate_name(async_mock_db):
    account_data = AccountCreate(name="Cash")

    # Simulate existing account found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=DBAccount(name="Cash"))
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc:
        await create_account(account_data, async_mock_db)

    assert exc.value.status_code == 400
    assert "already exists" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_update_account_success(async_mock_db):
    account_id = uuid.uuid4()
    existing_account = DBAccount(
        id=account_id,
        name="Old Name",
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    update_data = AccountUpdate(name="New Name", is_active=False)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing_account)
    async_mock_db.execute = AsyncMock(return_value=mock_result)
    async_mock_db.commit = AsyncMock()
    async_mock_db.refresh = AsyncMock()

    result = await update_account(account_id, update_data, async_mock_db)

    assert result.name == "New Name"
    assert result.is_active is False
    assert isinstance(result, AccountOut)


@pytest.mark.asyncio
async def test_update_account_not_found(async_mock_db):
    account_id = uuid.uuid4()
    update_data = AccountUpdate(name="New Name", is_active=True)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc:
        await update_account(account_id, update_data, async_mock_db)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


from app.services.account_service import list_active_accounts


@pytest.mark.asyncio
async def test_list_active_accounts(async_mock_db):
    mock_accounts = [
        DBAccount(
            id=uuid.uuid4(),
            name="Cash",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
        DBAccount(
            id=uuid.uuid4(),
            name="Sales Revenue",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        ),
    ]

    mock_result = MagicMock()
    mock_result.scalars = MagicMock(
        return_value=MagicMock(all=MagicMock(return_value=mock_accounts))
    )
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    response = await list_active_accounts(async_mock_db)

    assert isinstance(response, AccountListResponse)
    assert isinstance(response.accounts, list)
    assert len(response.accounts) == 2
    assert all(isinstance(a, AccountOut) for a in response.accounts)
