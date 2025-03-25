"""
File: accounts.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Handles creation, update, and retrieval of accounts.
"""

import logging
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.account_schema import (
    AccountCreate,
    AccountUpdate,
    AccountOut,
    AccountListResponse,
)
from app.services.account_service import (
    create_account,
    update_account,
    list_active_accounts,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post(
    "/",
    response_model=AccountOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description="Creates a new account for recording ledger entries.",
)
async def create_account_route(
    account: AccountCreate,
    db: AsyncSession = Depends(get_session),
) -> AccountOut:
    return await create_account(account, db)


@router.patch(
    "/{account_id}",
    response_model=AccountOut,
    summary="Update an account",
    description="Updates the name and/or active status of an existing account.",
)
async def update_account_route(
    account_id: str = Path(..., description="UUID of the account to update"),
    update: AccountUpdate = ...,
    db: AsyncSession = Depends(get_session),
) -> AccountOut:
    return await update_account(account_id, update, db)


@router.get(
    "/",
    response_model=AccountListResponse,
    summary="List active accounts",
    description="Retrieves all active accounts available for ledger entries.",
)
async def list_accounts_route(
    db: AsyncSession = Depends(get_session),
) -> AccountListResponse:
    return await list_active_accounts(db)
