"""
File: summary.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Handles summarization logic for ledger entries, including debit/credit totals and balance checks.
"""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.db.session import get_session
from app.services.summary_service import get_summary
from app.schemas.summary_schema import SummaryOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get(
    "/",
    response_model=SummaryOut,
    summary="Get a summary of the ledger",
    description=(
        "Returns total debit and credit amounts, counts, and balance check status."
    ),
)
async def get_summary_route(
    db: AsyncSession = Depends(get_session),
) -> SummaryOut:
    return await get_summary(
        db=db,
    )
