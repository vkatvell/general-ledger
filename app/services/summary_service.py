"""
File: summary_service.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Service functions for retreiving summary of balances for all ledger entries.
"""

import logging
from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.db_helpers import get_debit_credit_totals
from app.utils.ledger_helpers import normalize_entry_type

from app.db.models import DBLedgerEntry, DBAccount
from app.schemas.summary_schema import SummaryOut
from app.schemas.ledger_entry_schema import EntryType


async def get_summary(db: AsyncSession) -> SummaryOut:
    rows = await get_debit_credit_totals(db)

    # Set initial values
    num_debits = 0
    total_debit_amount = Decimal("0.00")
    num_credits = 0
    total_credit_amount = Decimal("0.00")

    # Handling different enum type in memory by collapsing into value
    for entry_type, count, total in rows:
        et = normalize_entry_type(entry_type)

        if et == EntryType.debit.value:
            num_debits = count
            total_debit_amount = total
        elif et == EntryType.credit.value:
            num_credits = count
            total_credit_amount = total

    return SummaryOut(
        num_debits=num_debits,
        total_debit_amount=total_debit_amount,
        num_credits=num_credits,
        total_credit_amount=total_credit_amount,
        is_balanced=(total_debit_amount == total_credit_amount),
    )
