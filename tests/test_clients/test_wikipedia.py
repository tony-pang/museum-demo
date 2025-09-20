"""Tests for Wikipedia client."""
import pytest
from unittest.mock import patch, AsyncMock
from src.clients.wikipedia import fetch_most_visited_museums


@pytest.mark.asyncio
async def test_fetch_most_visited_museums():
    """Test fetching most visited museums."""
    with patch('src.clients.wikipedia.httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"query": {"pages": []}}
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        result = await fetch_most_visited_museums()
        assert isinstance(result, list)
