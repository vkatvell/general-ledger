"""
File: account_schema.py
Author: Venkat Vellanki
Created: 2024-03-24
Last Modified: 2024-03-24
Description: Pydantic schema definitions for accounts, including models
             for account creation, retrieval, and optional update support.
             Used for input validation and API response serialization.
"""

from pydantic import BaseModel, ConfigDict

from uuid import UUID
from datetime import datetime


class AccountBase(BaseModel):
    name: str


class AccountCreate(AccountBase):
    """Schema for creating a new account."""

    pass


class AccountUpdate(BaseModel):
    """Optional future support for account updates."""

    name: str


class AccountOut(AccountBase):
    """Schema for returning account data in responses."""

    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
