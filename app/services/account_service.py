"""
File: account_service.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-26
Description: Service functions for creating, updating, and retrieving accounts.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from fastapi import HTTPException
from uuid import UUID

from app.db.models import DBAccount
from app.schemas.account_schema import (
    AccountCreate,
    AccountUpdate,
    AccountOut,
    AccountListResponse,
)
from app.utils.db_helpers import (
    get_account_or_raise_404,
    account_name_exists,
    get_account_by_name,
)
import logging
from sentry_sdk import capture_message, capture_exception

logger = logging.getLogger(__name__)


async def create_account(account: AccountCreate, db: AsyncSession) -> AccountOut:
    """Create a new account with the given name or reactivate if name already exists and is inactive."""
    logger.info("Attempting to create account: %s", account.name)
    existing = await get_account_by_name(account.name, db)

    if existing is None:
        # No conflict – create new account
        new_account = DBAccount(name=account.name, is_active=account.is_active)
        db.add(new_account)
        await db.commit()
        await db.refresh(new_account)
        logger.info("Created new account: %s", new_account.name)
        return AccountOut.model_validate(new_account)

    if existing.is_active:
        capture_message(
            f"Attempt to create duplicate active account: {account.name}",
            level="warning",
        )
        raise HTTPException(status_code=400, detail="Account name already exists")

    # Account exists but is inactive – reactivate
    existing.is_active = True
    await db.commit()
    await db.refresh(existing)
    logger.info("Reactivated inactive account: %s", existing.name)
    return AccountOut.model_validate(existing)


async def update_account(
    account_id: UUID, update: AccountUpdate, db: AsyncSession
) -> AccountOut:
    """Update an existing account's name or active status."""
    logger.info("Updating account_id=%s", account_id)
    account = await get_account_or_raise_404(account_id, db)

    if update.name and update.name != account.name:
        # Check for name conflict before applying the change
        if await account_name_exists(update.name, db):
            raise HTTPException(status_code=400, detail="Account name already exists")
        account.name = update.name

    if update.is_active is not None:
        account.is_active = update.is_active

    try:
        await db.commit()
        await db.refresh(account)
        logger.info("Updated account_id=%s", account.id)
        return AccountOut.model_validate(account)

    except IntegrityError as e:
        await db.rollback()
        capture_exception(e)
        raise HTTPException(status_code=400, detail="Account name already exists")


async def list_active_accounts(db: AsyncSession) -> AccountListResponse:
    """Return all active accounts for use in dropdowns or entry creation."""
    logger.info("Listing active accounts")
    stmt = (
        select(DBAccount)
        .where(DBAccount.is_active.is_(True))
        .order_by(DBAccount.name.asc())
    )
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return AccountListResponse(
        accounts=[AccountOut.model_validate(a) for a in accounts]
    )
