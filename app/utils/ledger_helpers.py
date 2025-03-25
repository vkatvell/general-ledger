from decimal import Decimal
from app.utils.currency import get_usd_to_cad_rate
from app.schemas.ledger_entry_schema import LedgerEntryOut
from app.db.models.ledger_entry_model import DBLedgerEntry


async def inject_cad_amount(entry: DBLedgerEntry) -> LedgerEntryOut:
    validated = LedgerEntryOut.model_validate(entry)
    usd_to_cad = await get_usd_to_cad_rate()
    validated.canadian_amount = round(validated.amount * Decimal(usd_to_cad), 2)
    return validated
