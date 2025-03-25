import asyncio
import uuid
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy import text

from app.db.session import async_session_factory
from app.db.models import DBAccount, DBLedgerEntry
from app.schemas.ledger_entry_schema import EntryType


async def seed(reset: bool = False):
    async with async_session_factory() as session:
        if reset:
            print("Resetting data...")
            await session.execute(
                text("TRUNCATE TABLE ledger_entries, accounts RESTART IDENTITY CASCADE")
            )
            await session.commit()
            session.expunge_all()

        # Create sample accounts
        accounts = [
            DBAccount(name="Cash", is_active=True),
            DBAccount(name="Bank", is_active=True),
            DBAccount(name="Accounts Receivable", is_active=True),
            DBAccount(name="Accounts Payable", is_active=True),
            DBAccount(name="Sales Revenue", is_active=True),
            DBAccount(name="Service Revenue", is_active=True),
            DBAccount(name="Rent Expense", is_active=True),
            DBAccount(name="Utilities Expense", is_active=True),
            DBAccount(name="Salaries Expense", is_active=True),
            DBAccount(name="Office Supplies", is_active=True),
            DBAccount(name="Equipment", is_active=True),
            DBAccount(
                name="Suspense", is_active=False
            ),  # Inactive account for edge case testing
        ]

        session.add_all(accounts)
        await session.flush()  # Ensures accounts get IDs

        # Build account_id lookup
        account_lookup = {acc.name: acc.id for acc in accounts}

        # Create sample ledger entries
        now = datetime.now(timezone.utc)
        entries = [
            DBLedgerEntry(
                account_id=account_lookup["Cash"],
                date=now,
                entry_type=EntryType.debit,
                amount=Decimal("5000.00"),
                currency="USD",
                description="Invoice #123",
                idempotency_key=str(uuid.uuid4()),
            ),
            DBLedgerEntry(
                account_id=account_lookup["Sales Revenue"],
                date=now,
                entry_type=EntryType.credit,
                amount=Decimal("5000.00"),
                currency="USD",
                description="Invoice #123 revenue",
                idempotency_key=str(uuid.uuid4()),
            ),
            DBLedgerEntry(
                account_id=account_lookup["Accounts Receivable"],
                date=now - timedelta(days=2),
                entry_type=EntryType.debit,
                amount=Decimal("1000.00"),
                currency="USD",
                description="Client deposit",
                idempotency_key=str(uuid.uuid4()),
            ),
            DBLedgerEntry(
                account_id=account_lookup["Cash"],
                date=now - timedelta(days=2),
                entry_type=EntryType.credit,
                amount=Decimal("1000.00"),
                currency="USD",
                description="Offset to cash",
                idempotency_key=str(uuid.uuid4()),
            ),
        ]

        session.add_all(entries)
        await session.commit()
        print(f"Seeded {len(accounts)} accounts and {len(entries)} ledger entries.")


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    asyncio.run(seed(reset=reset_flag))
