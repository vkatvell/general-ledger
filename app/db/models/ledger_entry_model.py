"""
File: ledger_entry.py
Author: Venkat Vellanki
Created: 2024-03-24
Last Modified: 2024-03-24
Description: SQLAlchemy model definition for LedgerEntry, representing
             debit/credit transactions with associated metadata and relationships.
"""

import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import (
    ForeignKey,
    String,
    Enum,
    Numeric,
    DateTime,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.db.session import Base
from app.db.models.account_model import DBAccount

from typing import Optional
import enum


class EntryType(enum.Enum):
    debit = "debit"
    credit = "credit"


class DBLedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    entry_type: Mapped[EntryType] = mapped_column(Enum(EntryType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    description: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(default=1)
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, nullable=True
    )

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_ledger_entry_idempotency_key"),
    )

    account: Mapped[DBAccount] = relationship(backref="entries")
