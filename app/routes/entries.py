"""
File: entries.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2024-03-25
Description: Handles creation, retrieval, update, and deletion of ledger entries.
"""

import logging
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.ledger_entry_schema import (
    LedgerEntryCreate,
    LedgerEntryUpdate,
    LedgerEntryOut,
)
from app.services.entry_service import (
    create_entry,
    list_entries,
    get_entry_by_id,
    update_entry,
    delete_entry,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/entries", tags=["Ledger Entries"])


@router.post(
    "/",
    response_model=LedgerEntryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ledger entry",
    description="Creates a new debit or credit entry in the general ledger.",
)
async def create_entry_route(
    entry: LedgerEntryCreate,
    db: AsyncSession = Depends(get_session),
) -> LedgerEntryOut:
    return await create_entry(entry, db)


@router.get(
    "/",
    response_model=list[LedgerEntryOut],
    summary="List all ledger entries",
    description="Retrieves all ledger entries, optionally filtered by account name, entry type, currency, or date range.",
)
async def list_entries_route(
    account_name: str | None = Query(default=None),
    currency: str | None = Query(default=None),
    entry_type: str | None = Query(default=None),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_session),
) -> list[LedgerEntryOut]:
    return await list_entries(
        db=db,
        account_name=account_name,
        currency=currency,
        entry_type=entry_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{entry_id}",
    response_model=LedgerEntryOut,
    summary="Retrieve a specific entry",
    description="Fetches a single ledger entry by its ID.",
)
async def get_entry_route(
    entry_id: str = Path(..., description="UUID of the ledger entry"),
    db: AsyncSession = Depends(get_session),
) -> LedgerEntryOut:
    return await get_entry_by_id(entry_id, db)


@router.patch(
    "/{entry_id}",
    response_model=LedgerEntryOut,
    summary="Update an existing entry",
    description="Updates the amount and/or description of a ledger entry. Other fields are immutable.",
)
async def update_entry_route(
    entry_id: str,
    update: LedgerEntryUpdate,
    db: AsyncSession = Depends(get_session),
) -> LedgerEntryOut:
    return await update_entry(entry_id, update, db)


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ledger entry",
    description="Marks the specified ledger entry as deleted.",
)
async def delete_entry_route(
    entry_id: str,
    db: AsyncSession = Depends(get_session),
) -> None:
    await delete_entry(entry_id, db)
