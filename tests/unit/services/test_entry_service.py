import pytest
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException
from app.schemas.ledger_entry_schema import (
    LedgerEntryCreate,
    EntryType,
    LedgerEntryOut,
    LedgerEntryUpdate,
    LedgerEntryDeletedResponse,
    LedgerEntryListResponse,
)
from app.services.entry_service import (
    create_entry,
    get_entry_by_id,
    update_entry,
    delete_entry,
    list_entries,
)
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
        idempotency_key=str(uuid.uuid4()),
    )

    # Setup account lookup
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)
    account_result = MagicMock()
    account_result.scalar_one_or_none.return_value = account

    # Setup idempotency check = no duplicate
    idempotency_result = MagicMock()
    idempotency_result.scalar_one_or_none.return_value = None

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
        idempotency_key=str(uuid.uuid4()),
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    async_mock_db.execute = AsyncMock(return_value=result)

    with pytest.raises(HTTPException) as exc:
        await create_entry(entry, async_mock_db)

    assert exc.value.status_code == 404
    assert "Account not found" in exc.value.detail


@pytest.mark.asyncio
async def test_create_entry_idempotent_conflict(async_mock_db):
    key = str(uuid.uuid4())
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
    account_result.scalar_one_or_none.return_value = account

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
    existing_result.scalar_one_or_none.return_value = existing

    async_mock_db.execute = AsyncMock(side_effect=[account_result, existing_result])

    with pytest.raises(HTTPException) as exc:
        await create_entry(entry, async_mock_db)

    assert exc.value.status_code == 409
    assert "Idempotency key already used" in exc.value.detail


@pytest.mark.asyncio
async def test_get_entry_by_id_success(async_mock_db):
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)
    entry_id = uuid.uuid4()

    entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.debit,
        amount=Decimal("100.00"),
        currency="USD",
        description="Valid entry",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=entry)
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    response = await get_entry_by_id(str(entry_id), async_mock_db)

    assert isinstance(response, LedgerEntryOut)
    assert response.id == entry.id
    assert response.account_name == account.name
    assert response.amount == Decimal("100.00")


@pytest.mark.asyncio
async def test_get_entry_by_id_not_found(async_mock_db):
    entry_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc:
        await get_entry_by_id(str(entry_id), async_mock_db)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_get_entry_by_id_soft_deleted(async_mock_db):
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)
    entry_id = uuid.uuid4()

    entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.credit,
        amount=Decimal("500.00"),
        currency="USD",
        description="Soft deleted entry",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=True,  # is_deleted is True, should not get entry
        version=1,
        account=account,
    )

    mock_result = MagicMock()
    # Simulating no entry returned
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    async_mock_db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(HTTPException) as exc:
        await get_entry_by_id(str(entry_id), async_mock_db)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_entry_success_amount_and_description(async_mock_db):
    entry_id = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.debit,
        amount=Decimal("100.00"),
        currency="USD",
        description="Old description",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )

    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=entry)
    async_mock_db.execute = AsyncMock(return_value=result)
    async_mock_db.commit = AsyncMock()
    async_mock_db.refresh = AsyncMock(side_effect=lambda e: e)

    update = LedgerEntryUpdate(
        amount=Decimal("200.00"),
        description="Updated description",
    )

    updated = await update_entry(str(entry_id), update, async_mock_db)

    assert updated.amount == Decimal("200.00")
    assert updated.description == "Updated description"
    assert updated.version == 2
    assert updated.account_name == "Cash"


@pytest.mark.asyncio
async def test_update_entry_partial_description_only(async_mock_db):
    entry_id = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.credit,
        amount=Decimal("500.00"),
        currency="USD",
        description="Old",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )

    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=entry)
    async_mock_db.execute = AsyncMock(return_value=result)
    async_mock_db.commit = AsyncMock()
    async_mock_db.refresh = AsyncMock(side_effect=lambda e: e)

    update = LedgerEntryUpdate(
        amount=None,
        description="New note only",
    )

    updated = await update_entry(str(entry_id), update, async_mock_db)

    assert updated.amount == Decimal("500.00")  # unchanged
    assert updated.description == "New note only"
    assert updated.version == 2


@pytest.mark.asyncio
async def test_update_entry_not_found(async_mock_db):
    entry_id = uuid.uuid4()
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)

    async_mock_db.execute = AsyncMock(return_value=result)

    update = LedgerEntryUpdate(amount=Decimal("100.00"))

    with pytest.raises(HTTPException) as exc:
        await update_entry(str(entry_id), update, async_mock_db)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_entry_soft_deleted_excluded(async_mock_db):
    entry_id = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    soft_deleted_entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.debit,
        amount=Decimal("100.00"),
        currency="USD",
        description="Old",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=True,
        version=1,
        account=account,
    )

    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)  # filtered out by query
    async_mock_db.execute = AsyncMock(return_value=result)

    update = LedgerEntryUpdate(description="Should not update")

    with pytest.raises(HTTPException) as exc:
        await update_entry(str(entry_id), update, async_mock_db)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_entry_no_changes_provided(async_mock_db):
    entry_id = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.debit,
        amount=Decimal("500.00"),
        currency="USD",
        description="Same",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )

    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=entry)
    async_mock_db.execute = AsyncMock(return_value=result)

    update = LedgerEntryUpdate()  # nothing to update

    with pytest.raises(HTTPException) as exc:
        await update_entry(str(entry_id), update, async_mock_db)

    assert exc.value.status_code == 400
    assert "no fields" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_update_entry_same_data_raises(async_mock_db):
    entry_id = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.credit,
        amount=Decimal("100.00"),
        currency="USD",
        description="Original",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )

    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=entry)
    async_mock_db.execute = AsyncMock(return_value=result)

    update = LedgerEntryUpdate(
        amount=Decimal("100.00"),  # same
        description="Original",  # same
    )

    with pytest.raises(HTTPException) as exc:
        await update_entry(str(entry_id), update, async_mock_db)

    assert exc.value.status_code == 400
    assert "no changes" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_delete_entry_success(async_mock_db):
    entry_id = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    entry = DBLedgerEntry(
        id=entry_id,
        account_id=account.id,
        entry_type=EntryType.debit,
        amount=Decimal("300.00"),
        currency="USD",
        description="To be deleted",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )

    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=entry)

    async_mock_db.execute = AsyncMock(return_value=result)
    async_mock_db.commit = AsyncMock()
    async_mock_db.refresh = AsyncMock(side_effect=lambda e: e)

    deleted = await delete_entry(str(entry_id), async_mock_db)

    assert isinstance(deleted, LedgerEntryDeletedResponse)
    assert deleted.id == entry_id
    assert deleted.is_deleted is True
    assert deleted.version == 2


@pytest.mark.asyncio
async def test_delete_entry_not_found(async_mock_db):
    entry_id = uuid.uuid4()

    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)

    async_mock_db.execute = AsyncMock(return_value=result)

    with pytest.raises(HTTPException) as exc:
        await delete_entry(str(entry_id), async_mock_db)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_delete_entry_already_deleted(async_mock_db):
    entry_id = uuid.uuid4()
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    # Simulate already deleted entry excluded by query
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)

    async_mock_db.execute = AsyncMock(return_value=result)

    with pytest.raises(HTTPException) as exc:
        await delete_entry(str(entry_id), async_mock_db)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_list_entries_basic(async_mock_db):
    account = DBAccount(id=uuid.uuid4(), name="Cash", is_active=True)

    entry = DBLedgerEntry(
        id=uuid.uuid4(),
        account_id=account.id,
        entry_type=EntryType.debit,
        amount=Decimal("50.00"),
        currency="USD",
        description="Listed",
        idempotency_key=str(uuid.uuid4()),
        date=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        is_deleted=False,
        version=1,
        account=account,
    )

    # Mock count first, then entries
    async_mock_db.execute = AsyncMock(
        side_effect=[
            MagicMock(scalar_one=MagicMock(return_value=1)),  # count
            MagicMock(
                scalars=MagicMock(
                    return_value=MagicMock(all=MagicMock(return_value=[entry]))
                )
            ),  # entries
        ]
    )

    entries = await list_entries(
        db=async_mock_db,
        account_name="Cash",
        currency="USD",
        entry_type="debit",
        start_date=None,
        end_date=None,
        limit=10,
        offset=0,
    )

    assert isinstance(entries, LedgerEntryListResponse)
    assert entries.total == 1
    assert isinstance(entries.entries, list)
    assert entries.entries[0].account_name == "Cash"
    assert entries.entries[0].amount == Decimal("50.00")


@pytest.mark.asyncio
async def test_list_entries_empty_result(async_mock_db):
    async_mock_db.execute = AsyncMock(
        side_effect=[
            MagicMock(scalar_one=MagicMock(return_value=0)),  # count
            MagicMock(
                scalars=MagicMock(
                    return_value=MagicMock(all=MagicMock(return_value=[]))
                )
            ),  # entries
        ]
    )

    result = await list_entries(
        db=async_mock_db,
        account_name="Ghost",
        currency="USD",
        entry_type="credit",
    )

    assert isinstance(result, LedgerEntryListResponse)
    assert result.total == 0
    assert result.entries == []
