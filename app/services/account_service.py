"""
File: account_service.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Service functions for creating, updating, and retrieving accounts.
"""

from sqlalchemy.ext.asyncio import AsyncSession
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


async def create_account(account: AccountCreate, db: AsyncSession) -> AccountOut:
    """Create a new account with the given name."""
    # Check if account name already exists
    result = await db.execute(select(DBAccount).where(DBAccount.name == account.name))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Account name already exists")

    new_account = DBAccount(name=account.name, is_active=account.is_active)
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return AccountOut.model_validate(new_account)


async def update_account(
    account_id: UUID, update: AccountUpdate, db: AsyncSession
) -> AccountOut:
    """Update an existing account's name or active status."""
    stmt = select(DBAccount).where(DBAccount.id == account_id)
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if update.name:
        account.name = update.name
    if update.is_active is not None:
        account.is_active = update.is_active

    await db.commit()
    await db.refresh(account)
    return AccountOut.model_validate(account)


async def list_active_accounts(db: AsyncSession) -> AccountListResponse:
    """Return all active accounts for use in dropdowns or entry creation."""
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
