"""
File: summary_schema.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Pydantic schema for ledger summary response.
"""

from decimal import Decimal
from pydantic import BaseModel, Field


class SummaryOut(BaseModel):
    """Represents an aggregated summary of debit and credit entries."""

    num_debits: int = Field(..., ge=0, description="Number of debit entries")
    total_debit_amount: Decimal = Field(
        ..., ge=0, description="Sum of all debit amounts"
    )
    num_credits: int = Field(..., ge=0, description="Number of credit entries")
    total_credit_amount: Decimal = Field(
        ..., ge=0, description="Sum of all credit amounts"
    )
    is_balanced: bool = Field(
        ..., description="True if total debits equal total credits"
    )
