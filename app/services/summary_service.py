"""
File: summary_service.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Service functions for retreiving summary of balances for an account.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DBLedgerEntry, DBAccount
from app.schemas.summary_schema import SummaryOut
from app.schemas.ledger_entry_schema import EntryType


async def get_summary(
    db: AsyncSession,
    account_name: Optional[str] = None,
    currency: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> SummaryOut:
    filters = [DBLedgerEntry.is_deleted == False]

    if account_name:
        stmt = select(DBAccount.id).where(
            DBAccount.name == account_name, DBAccount.is_active == True
        )
        result = await db.execute(stmt)
        account_row = await result.first()
        if not account_row:
            return SummaryOut(
                num_debits=0,
                total_debit_amount=Decimal("0.00"),
                num_credits=0,
                total_credit_amount=Decimal("0.00"),
                is_balanced=True,
            )
        account_id = account_row[0]
        filters.append(DBLedgerEntry.account_id == account_id)

    if currency:
        filters.append(DBLedgerEntry.currency == currency.upper())

    if start_date:
        filters.append(DBLedgerEntry.date >= start_date)
    if end_date:
        filters.append(DBLedgerEntry.date <= end_date)

    stmt = (
        select(
            DBLedgerEntry.entry_type,
            func.count().label("count"),
            func.coalesce(func.sum(DBLedgerEntry.amount), Decimal("0.00")).label(
                "total"
            ),
        )
        .where(and_(*filters))
        .group_by(DBLedgerEntry.entry_type)
    )

    result = await db.execute(stmt)
    rows = await result.all()

    summary = {
        EntryType.debit: {"count": 0, "total": Decimal("0.00")},
        EntryType.credit: {"count": 0, "total": Decimal("0.00")},
    }

    for entry_type, count, total in rows:
        summary[entry_type]["count"] = count
        summary[entry_type]["total"] = total

    is_balanced = (
        summary[EntryType.debit]["total"] == summary[EntryType.credit]["total"]
    )

    return SummaryOut(
        num_debits=summary[EntryType.debit]["count"],
        total_debit_amount=summary[EntryType.debit]["total"],
        num_credits=summary[EntryType.credit]["count"],
        total_credit_amount=summary[EntryType.credit]["total"],
        is_balanced=is_balanced,
    )
