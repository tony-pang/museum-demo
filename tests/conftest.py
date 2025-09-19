"""Pytest configuration and fixtures."""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_wikipedia_response():
    """Mock Wikipedia API response."""
    return {
        "parse": {
            "text": {
                "*": """
                <table class="wikitable sortable">
                <thead><tr><th>Museum</th><th>Visitors</th><th>City</th><th>Country</th></tr></thead>
                <tbody>
                <tr><td>Louvre</td><td>9,600,000 (2023)</td><td>Paris</td><td>France</td></tr>
                <tr><td>Metropolitan Museum</td><td>6,479,548 (2023)</td><td>New York</td><td>United States</td></tr>
                <tr><td>British Museum</td><td>5,820,860 (2023)</td><td>London</td><td>United Kingdom</td></tr>
                </tbody>
                </table>
                """
            }
        }
    }


@pytest.fixture
def mock_wikidata_response():
    """Mock Wikidata SPARQL response."""
    return {
        "results": {
            "bindings": [
                {
                    "city": {"value": "Paris"},
                    "population": {"value": "11000000"},
                    "year": {"value": "2023"},
                    "wikidata_id": {"value": "Q90"}
                },
                {
                    "city": {"value": "New York"},
                    "population": {"value": "8336817"},
                    "year": {"value": "2023"},
                    "wikidata_id": {"value": "Q60"}
                },
                {
                    "city": {"value": "London"},
                    "population": {"value": "8982000"},
                    "year": {"value": "2023"},
                    "wikidata_id": {"value": "Q84"}
                }
            ]
        }
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for external API calls."""
    mock_client = AsyncMock()
    
    # Mock Wikipedia API response
    wikipedia_response = AsyncMock()
    wikipedia_response.status_code = 200
    wikipedia_response.json = AsyncMock(return_value={
        "parse": {
            "text": {
                "*": """
                <table class="wikitable sortable">
                <thead><tr><th>Museum</th><th>Visitors</th><th>City</th><th>Country</th></tr></thead>
                <tbody>
                <tr><td>Louvre</td><td>9,600,000 (2023)</td><td>Paris</td><td>France</td></tr>
                <tr><td>Metropolitan Museum</td><td>6,479,548 (2023)</td><td>New York</td><td>United States</td></tr>
                </tbody>
                </table>
                """
            }
        }
    })
    
    # Mock Wikidata SPARQL response
    wikidata_response = AsyncMock()
    wikidata_response.status_code = 200
    wikidata_response.json = AsyncMock(return_value={
        "results": {
            "bindings": [
                {
                    "city": {"value": "Paris"},
                    "population": {"value": "11000000"},
                    "year": {"value": "2023"},
                    "wikidata_id": {"value": "Q90"}
                },
                {
                    "city": {"value": "New York"},
                    "population": {"value": "8336817"},
                    "year": {"value": "2023"},
                    "wikidata_id": {"value": "Q60"}
                }
            ]
        }
    })
    
    # Configure mock client to return different responses based on URL
    async def mock_get(url, **kwargs):
        if "wikipedia.org" in url:
            return wikipedia_response
        elif "wikidata.org" in url:
            return wikidata_response
        else:
            raise ValueError(f"Unexpected URL: {url}")
    
    mock_client.get = mock_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    
    return mock_client


@pytest.fixture
def mock_database():
    """Mock database operations."""
    with patch('src.db.session.SessionLocal') as mock_session:
        mock_db = AsyncMock()
        mock_session.return_value = mock_db
        yield mock_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()