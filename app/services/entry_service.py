"""
File: entry_service.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Service functions for creating, retrieving, updating, and deleting ledger entries.
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models.ledger_entry_model import DBLedgerEntry
from app.db.models.account_model import DBAccount
from app.schemas.ledger_entry_schema import (
    LedgerEntryCreate,
    LedgerEntryOut,
    LedgerEntryUpdate,
)


async def create_entry(entry: LedgerEntryCreate, db: AsyncSession) -> LedgerEntryOut:
    """Create a new ledger entry after validating account and input rules."""
    # Validate account
    result = await db.execute(
        select(DBAccount).where(
            DBAccount.name == entry.account_name, DBAccount.is_active.is_(True)
        )
    )
    account = await result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or inactive")

    # Check idempotency key: if an entry with same key already exists
    existing = await db.execute(
        select(DBLedgerEntry).where(
            DBLedgerEntry.idempotency_key == entry.idempotency_key
        )
    )
    existing_entry = await existing.scalar_one_or_none()

    if existing_entry:
        # Strict idempotency enforcement: reject if any data differs
        if (
            existing_entry.account_id != account.id
            or existing_entry.entry_type != entry.entry_type
            or existing_entry.amount != entry.amount
            or existing_entry.currency != entry.currency
            or (existing_entry.description or "") != (entry.description or "")
        ):
            raise HTTPException(
                status_code=409,  # Conflict status code
                detail="Idempotency key already used with different data",
            )
        return LedgerEntryOut.model_validate(existing_entry)

    # Create DB object
    new_entry = DBLedgerEntry(
        account_id=account.id,
        entry_type=entry.entry_type,
        amount=entry.amount,
        currency=entry.currency,
        description=entry.description,
        date=entry.date or datetime.now(timezone.utc),
        idempotency_key=entry.idempotency_key,
    )
    await db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return LedgerEntryOut.model_validate(new_entry)


async def get_entry_by_id(entry_id: str, db: AsyncSession) -> LedgerEntryOut:
    """Fetch a single ledger entry by ID, excluding soft-deleted records."""
    result = await db.execute(
        select(DBLedgerEntry)
        .options(joinedload(DBLedgerEntry.account))
        .where(DBLedgerEntry.id == entry_id, DBLedgerEntry.is_deleted.is_(False))
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return LedgerEntryOut.model_validate(entry)


async def list_entries(
    db: AsyncSession,
    account_name: str | None = None,
    currency: str | None = None,
    entry_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[LedgerEntryOut]:
    """Retrieve all ledger entries with optional filters."""
    stmt = select(DBLedgerEntry).where(DBLedgerEntry.is_deleted.is_(False))

    if account_name:
        stmt = stmt.join(DBLedgerEntry.account).where(DBAccount.name == account_name)
    if currency:
        stmt = stmt.where(DBLedgerEntry.currency == currency)
    if entry_type:
        stmt = stmt.where(DBLedgerEntry.entry_type == entry_type)
    if start_date:
        stmt = stmt.where(DBLedgerEntry.timestamp >= start_date)
    if end_date:
        stmt = stmt.where(DBLedgerEntry.timestamp <= end_date)

    stmt = stmt.order_by(DBLedgerEntry.timestamp.desc()).offset(offset).limit(limit)
    results = (await db.execute(stmt)).scalars().all()
    return [LedgerEntryOut.model_validate(e) for e in results]


async def update_entry(
    entry_id: str, update: LedgerEntryUpdate, db: AsyncSession
) -> LedgerEntryOut:
    """Update the amount or description of an existing ledger entry."""
    result = await db.execute(
        select(DBLedgerEntry).where(
            DBLedgerEntry.id == entry_id, DBLedgerEntry.is_deleted.is_(False)
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    if update.amount is not None:
        entry.amount = update.amount
    if update.description is not None:
        entry.description = update.description
    entry.updated_at = datetime.now(timezone.utc)
    entry.version += 1

    await db.commit()
    await db.refresh(entry)
    return LedgerEntryOut.model_validate(entry)


async def delete_entry(entry_id: str, db: AsyncSession) -> None:
    """Soft-delete a ledger entry by marking it as deleted."""
    result = await db.execute(
        select(DBLedgerEntry).where(
            DBLedgerEntry.id == entry_id, DBLedgerEntry.is_deleted.is_(False)
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    entry.is_deleted = True
    entry.updated_at = datetime.now(timezone.utc)
    entry.version += 1

    await db.commit()
