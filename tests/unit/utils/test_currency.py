import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.utils.currency import get_usd_to_cad_rate


@pytest.mark.asyncio
async def test_get_usd_to_cad_rate_success():
    mock_json = {
        "data": [
            {
                "country_currency_desc": "Canada-Dollar",
                "exchange_rate": "1.438",
                "record_date": "2024-12-31",
            }
        ]
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(return_value=mock_json)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response
        rate = await get_usd_to_cad_rate()

    assert rate == 1.438
