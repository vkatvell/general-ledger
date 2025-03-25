"""
File: account_model.py
Author: Venkat Vellanki
Created: 2024-03-24
Last Modified: 2024-03-25
Description: SQLAlchemy model definition for Account entity, which holds
             user-defined account names and links to ledger entries.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List
from app.db.session import Base


class DBAccount(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    entries: Mapped[list["DBLedgerEntry"]] = relationship(back_populates="account")


# Avoiding circular imports
from app.db.models.ledger_entry_model import DBLedgerEntry
