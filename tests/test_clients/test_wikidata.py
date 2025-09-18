"""Tests for Wikidata client."""
import pytest
from unittest.mock import patch, AsyncMock
from src.clients.wikidata import fetch_city_population


@pytest.mark.asyncio
async def test_fetch_city_population():
    """Test fetching city population from Wikidata."""
    with patch('src.clients.wikidata.httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {"bindings": []}}
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await fetch_city_population("Q90")
        assert isinstance(result, dict)
