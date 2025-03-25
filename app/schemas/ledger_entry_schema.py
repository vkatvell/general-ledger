"""
File: ledger_entry_schema.py
Author: Venkat Vellanki
Created: 2024-03-24
Last Modified: 2024-03-25
Description: Pydantic schema definitions for ledger entries, including models
             for creating, updating, and serializing debit and credit records
             within the general ledger system.
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from datetime import datetime


class EntryType(str, Enum):
    debit = "debit"
    credit = "credit"


class LedgerEntryBase(BaseModel):
    account_name: str = Field(..., description="Name of the account (e.g., 'Cash')")
    date: Optional[datetime] = Field(
        None, description="Ledger transaction date. Defaults to current UTC time."
    )
    entry_type: EntryType = Field(..., description="Type of entry: debit or credit")
    amount: Decimal = Field(..., ge=0, description="Amount (must be ≥ 0)")
    currency: str = Field(
        ..., min_length=3, max_length=3, description="Currency code (e.g., 'USD')"
    )
    description: Optional[str] = Field(None, description="Optional description")
    idempotency_key: UUID = Field(
        ..., description="Idempotency key to prevent duplicates"
    )


class LedgerEntryCreate(LedgerEntryBase):
    pass


class LedgerEntryUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None


class LedgerEntryDeletedResponse(BaseModel):
    id: UUID
    is_deleted: bool
    version: int

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryOut(LedgerEntryBase):
    id: UUID
    account_id: UUID
    account_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    version: int

    model_config = ConfigDict(from_attributes=True)


class LedgerEntryListResponse(BaseModel):
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    entries: List[LedgerEntryOut]
