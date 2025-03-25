"""
File: currency.py
Author: Venkat Vellanki
Created: 2025-03-25
Last Modified: 2025-03-25
Description: Utility function for fetching the latest available USD -> CAD exchange
             rate from the Treasury API.
"""

import httpx
from datetime import date
from decimal import Decimal


TREASURY_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/"
    "rates_of_exchange?fields=country_currency_desc,exchange_rate,record_date"
    "&filter=country_currency_desc:eq:Canada-Dollar"
    "&sort=-record_date&page[size]=1"
)


async def get_usd_to_cad_rate() -> float:
    """Fetch latest available USD → CAD exchange rate from the Treasury API."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(TREASURY_URL)
        response.raise_for_status()
        data = response.json()

    try:
        rate_str = data["data"][0]["exchange_rate"]
        return float(rate_str)
    except (KeyError, IndexError, ValueError):
        raise RuntimeError("Failed to parse exchange rate for Canada-Dollar")
