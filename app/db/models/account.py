"""
File: account.py
Author: Venkat Vellanki
Created: 2024-03-24
Last Modified: 2024-03-24
Description: SQLAlchemy model definition for Account entity, which holds
             user-defined account names and links to ledger entries.
"""

import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.db.session import Base


class DBAccount(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[str] = mapped_column(server_default="now()")

    entries: Mapped[List["DBLedgerEntry"]] = relationship(back_populates="account")


# Avoiding circular imports
from app.db.models.ledger_entry import DBLedgerEntry
