"""
File: entry_service.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Service functions for creating, retrieving, updating, and deleting ledger entries.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utils.currency import get_usd_to_cad_rate
from app.db.models.ledger_entry_model import DBLedgerEntry
from app.db.models.account_model import DBAccount
from app.schemas.ledger_entry_schema import (
    LedgerEntryCreate,
    LedgerEntryOut,
    LedgerEntryUpdate,
    LedgerEntryDeletedResponse,
    EntryType,
    LedgerEntryListResponse,
)


async def create_entry(entry: LedgerEntryCreate, db: AsyncSession) -> LedgerEntryOut:
    """Create a new ledger entry after validating account and input rules."""
    # Validate account
    result = await db.execute(
        select(DBAccount).where(
            DBAccount.name == entry.account_name, DBAccount.is_active.is_(True)
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or inactive")

    # Check idempotency key: if an entry with same key already exists
    existing = await db.execute(
        select(DBLedgerEntry).where(
            DBLedgerEntry.idempotency_key == str(entry.idempotency_key)
        )
    )
    existing_entry = existing.scalar_one_or_none()

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
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)

    # Injecting USD -> CAD conversion
    usd_entry = LedgerEntryOut.model_validate(new_entry)
    usd_to_cad = await get_usd_to_cad_rate()
    usd_entry.canadian_amount = round(usd_entry.amount * Decimal(usd_to_cad), 2)
    return usd_entry


async def get_entry_by_id(entry_id: str, db: AsyncSession) -> LedgerEntryOut:
    """Fetch a single ledger entry by ID, excluding deleted records."""
    stmt = (
        select(DBLedgerEntry)
        .options(
            selectinload(DBLedgerEntry.account)
        )  # eager loading needed for account_name
        .where(DBLedgerEntry.id == entry_id, DBLedgerEntry.is_deleted.is_(False))
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()

    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    usd_entry = LedgerEntryOut.model_validate(entry)
    usd_to_cad = await get_usd_to_cad_rate()
    usd_entry.canadian_amount = round(usd_entry.amount * Decimal(usd_to_cad), 2)
    return usd_entry


async def update_entry(
    entry_id: str, update: LedgerEntryUpdate, db: AsyncSession
) -> LedgerEntryOut:
    """Update the amount or description of an existing ledger entry."""
    if update.amount is None and update.description is None:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    stmt = (
        select(DBLedgerEntry)
        .options(
            selectinload(DBLedgerEntry.account)
        )  # eager loading needed for account_name
        .where(DBLedgerEntry.id == entry_id, DBLedgerEntry.is_deleted.is_(False))
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")

    # Check if any actual change is being made
    changes_detected = False

    if update.amount is not None and update.amount != entry.amount:
        changes_detected = True

    if update.description is not None and (update.description or "") != (
        entry.description or ""
    ):
        changes_detected = True

    if not changes_detected:
        raise HTTPException(status_code=400, detail="No changes detected in update")

    # Apply changes
    if update.amount is not None:
        entry.amount = update.amount
    if update.description is not None:
        entry.description = update.description
    entry.updated_at = datetime.now(timezone.utc)
    entry.version += 1

    await db.commit()
    await db.refresh(entry)

    # Injecting USD -> CAD conversion
    usd_entry = LedgerEntryOut.model_validate(entry)
    usd_to_cad = await get_usd_to_cad_rate()
    usd_entry.canadian_amount = round(usd_entry.amount * Decimal(usd_to_cad), 2)
    return usd_entry


async def delete_entry(entry_id: str, db: AsyncSession) -> LedgerEntryDeletedResponse:
    """Soft-delete a ledger entry by marking it as deleted and reutrn confirmation metadata."""
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
    await db.refresh(entry)

    return LedgerEntryDeletedResponse.model_validate(entry)


async def list_entries(
    db: AsyncSession,
    account_name: str | None = None,
    currency: str | None = None,
    entry_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> LedgerEntryListResponse:
    """Retrieve all ledger entries with optional filters."""
    stmt = (
        select(DBLedgerEntry)
        .options(selectinload(DBLedgerEntry.account))
        .where(DBLedgerEntry.is_deleted.is_(False))
    )

    # Case insensitive filtering
    if account_name:
        stmt = stmt.join(DBAccount).where(
            func.lower(DBAccount.name) == account_name.lower()
        )
    if currency:
        stmt = stmt.where(DBLedgerEntry.currency == currency.upper())
    if entry_type:
        stmt = stmt.where(DBLedgerEntry.entry_type == EntryType(entry_type))
    if start_date:
        stmt = stmt.where(DBLedgerEntry.date >= datetime.fromisoformat(start_date))
    if end_date:
        stmt = stmt.where(DBLedgerEntry.date <= datetime.fromisoformat(end_date))

    # Get total count before applying offset/limit
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar_one()

    # Apply pagination
    stmt = stmt.order_by(DBLedgerEntry.date.desc()).offset(offset).limit(limit)
    results = (await db.execute(stmt)).scalars().all()

    # Fetch USD -> CAD exchange rate
    usd_to_cad = await get_usd_to_cad_rate()

    # Inject canadian_amount in each response object
    entries: List[LedgerEntryOut] = []
    for e in results:
        validated = LedgerEntryOut.model_validate(e)
        validated.canadian_amount = round(validated.amount * Decimal(usd_to_cad), 2)
        entries.append(validated)
    return LedgerEntryListResponse(
        total=total, limit=limit, offset=offset, entries=entries
    )
