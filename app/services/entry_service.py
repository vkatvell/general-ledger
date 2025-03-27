"""
File: entry_service.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-26
Description: Service functions for creating, retrieving, updating, and deleting ledger entries.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.utils.ledger_helpers import inject_cad_amount, get_usd_to_cad_rate
from app.utils.db_helpers import get_entry_or_raise_404, get_active_account_by_name
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
from sentry_sdk import capture_message
import logging

logger = logging.getLogger(__name__)


async def create_entry(entry: LedgerEntryCreate, db: AsyncSession) -> LedgerEntryOut:
    """Create a new ledger entry after validating account and input rules."""
    logger.info("Creating ledger entry with idempotency_key=%s", entry.idempotency_key)
    # Validate account
    account = await get_active_account_by_name(entry.account_name, db)

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
            capture_message(
                f"Idempotency conflict: key={entry.idempotency_key}", level="warning"
            )
            raise HTTPException(
                status_code=409,  # Conflict status code
                detail="Idempotency key already used with different data",
            )
        logger.info("Idempotency match found. Returning existing entry.")
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

    # Injecting USD -> CAD conversion into entry
    usd_entry = await inject_cad_amount(new_entry)
    logger.info(
        "Ledger entry created successfully: idempotency_key=%s", entry.idempotency_key
    )
    return usd_entry


async def get_entry_by_id(entry_id: str, db: AsyncSession) -> LedgerEntryOut:
    """Fetch a single ledger entry by ID, excluding deleted records."""
    entry = await get_entry_or_raise_404(entry_id, db)
    # Injecting USD -> CAD conversion into entry
    usd_entry = await inject_cad_amount(entry)
    return usd_entry


async def update_entry(
    entry_id: str, update: LedgerEntryUpdate, db: AsyncSession
) -> LedgerEntryOut:
    """Update the amount or description of an existing ledger entry."""
    if update.amount is None and update.description is None:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    entry = await get_entry_or_raise_404(entry_id, db)

    # Check if any actual change is being made
    changes_detected = False

    if update.amount is not None and update.amount != entry.amount:
        changes_detected = True

    if update.description is not None and (update.description or "") != (
        entry.description or ""
    ):
        changes_detected = True

    if not changes_detected:
        capture_message(f"No changes detected in update", level="warning")
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

    logger.info("Successfully updated entry_id=%s", entry_id)

    # Injecting USD -> CAD conversion into entry
    usd_entry = await inject_cad_amount(entry)
    return usd_entry


async def delete_entry(entry_id: str, db: AsyncSession) -> LedgerEntryDeletedResponse:
    """Soft-delete a ledger entry by marking it as deleted and reutrn confirmation metadata."""
    logger.info("Attempting to delete entry_id=%s", entry_id)

    entry = await get_entry_or_raise_404(entry_id, db)

    entry.is_deleted = True
    entry.updated_at = datetime.now(timezone.utc)
    entry.version += 1

    await db.commit()
    await db.refresh(entry)

    logger.info("Successfully soft-deleted entry_id=%s", entry_id)
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
    try:
        if start_date:
            stmt = stmt.where(DBLedgerEntry.date >= datetime.fromisoformat(start_date))
        if end_date:
            stmt = stmt.where(DBLedgerEntry.date <= datetime.fromisoformat(end_date))
    except ValueError as e:
        capture_message(f"{e}", level="warning")
        raise HTTPException(status_code=400, detail="Invalid date format")

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
