"""
File: account_schema.py
Author: Venkat Vellanki
Created: 2024-03-24
Last Modified: 2024-03-24
Description: Pydantic schema definitions for accounts, including models
             for account creation, retrieval, and optional update support.
             Used for input validation and API response serialization.
"""

from pydantic import BaseModel, ConfigDict, Field

from uuid import UUID
from datetime import datetime
from typing import Optional, List


class AccountBase(BaseModel):
    name: str = Field(..., description="The name of the account (e.g., 'Cash')")


class AccountCreate(AccountBase):
    """Schema for creating a new account."""

    is_active: Optional[bool] = Field(
        default=True, description="Whether the account is active"
    )


class AccountUpdate(BaseModel):
    """Schema for partially updating an account."""

    name: Optional[str] = Field(None, description="New name for the account")
    is_active: Optional[bool] = Field(None, description="Set account active/inactive")


class AccountOut(AccountBase):
    """Schema for returning account data in responses."""

    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountListResponse(BaseModel):
    """Schema for listing multiple accounts (e.g. in dropdowns)."""

    accounts: List[AccountOut]
