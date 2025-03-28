"""
File: ledger_helpers.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Helper functions related to ledger logic, including CAD conversion
             injection and aggregation logic for summaries. Used by entry and
             summary services to enforce consistency.
"""

from decimal import Decimal
from app.utils.currency import get_usd_to_cad_rate
from app.schemas.ledger_entry_schema import LedgerEntryOut, EntryType
from app.db.models.ledger_entry_model import DBLedgerEntry


async def inject_cad_amount(entry: DBLedgerEntry) -> LedgerEntryOut:
    """Add a computed CAD amount to a validated ledger entry."""
    validated = LedgerEntryOut.model_validate(entry)
    usd_to_cad = await get_usd_to_cad_rate()
    validated.canadian_amount = round(validated.amount * Decimal(usd_to_cad), 2)
    return validated


def normalize_entry_type(value: str | EntryType) -> str:
    """Ensure consistent string value for entry_type."""
    return getattr(value, "value", value)
