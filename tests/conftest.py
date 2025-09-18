"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def sample_museum_data():
    """Sample museum data for testing."""
    return {
        "museum_id": 1,
        "museum_name": "Louvre",
        "city_id": 1,
        "city_name": "Paris",
        "year": 2023,
        "visitors": 10000000,
        "population": 11000000
    }
