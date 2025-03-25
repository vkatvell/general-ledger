from decimal import Decimal
from uuid import UUID
from fastapi import HTTPException

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.ledger_entry_model import DBLedgerEntry
from app.db.models.account_model import DBAccount


async def get_entry_or_raise_404(entry_id: str, db: AsyncSession) -> DBLedgerEntry:
    """Fetch a ledger entry or raise 404 if not found or deleted."""
    stmt = (
        select(DBLedgerEntry)
        .options(selectinload(DBLedgerEntry.account))
        .where(DBLedgerEntry.id == entry_id, DBLedgerEntry.is_deleted.is_(False))
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Ledger entry not found")
    return entry


async def get_debit_credit_totals(db: AsyncSession) -> list[tuple[str, int, Decimal]]:
    """Return counts and totals grouped by entry type."""
    stmt = (
        select(
            DBLedgerEntry.entry_type,
            func.count().label("count"),
            func.coalesce(func.sum(DBLedgerEntry.amount), Decimal("0.00")).label(
                "total"
            ),
        )
        .where(DBLedgerEntry.is_deleted.is_(False))
        .group_by(DBLedgerEntry.entry_type)
    )
    result = await db.execute(stmt)
    return result.all()


async def get_account_or_raise_404(account_id: UUID, db: AsyncSession) -> DBAccount:
    """Fetch an account by ID or raise 404 if not found."""
    result = await db.execute(select(DBAccount).where(DBAccount.id == account_id))
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


async def account_name_exists(name: str, db: AsyncSession) -> bool:
    """Check if an account name already exists."""
    result = await db.execute(select(DBAccount).where(DBAccount.name == name))
    return result.scalar_one_or_none() is not None


async def get_active_account_by_name(name: str, db: AsyncSession) -> DBAccount:
    """Fetch an active account by name or raise 404."""
    result = await db.execute(
        select(DBAccount).where(DBAccount.name == name, DBAccount.is_active.is_(True))
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or inactive")
    return account
