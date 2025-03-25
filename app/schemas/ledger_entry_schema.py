"""
File: ledger_entry_schema.py
Author: Venkat Vellanki
Created: 2024-03-24
Last Modified: 2024-03-24
Description: Pydantic schema definitions for ledger entries, including models
             for creating, updating, and serializing debit and credit records
             within the general ledger system.
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal
from enum import Enum
from typing import Optional
from datetime import datetime


class EntryType(str, Enum):
    debit = "debit"
    credit = "credit"


class LedgerEntryBase(BaseModel):
    account_id: UUID
    entry_type: EntryType
    amount: Decimal = Field(..., ge=0)
    currency: str = "USD"
    description: Optional[str] = None


class LedgerEntryCreate(LedgerEntryBase):
    pass


class LedgerEntryUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None


class LedgerEntryOut(LedgerEntryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    version: int

    model_config = ConfigDict(from_attributes=True)
