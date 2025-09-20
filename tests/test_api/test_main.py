"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app


def test_healthcheck(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_features_empty(client: TestClient):
    """Test features endpoint returns empty dataset structure."""
    response = client.get("/features")
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "rows" in data
    assert data["rows"] == []
    expected_columns = ["museum_id", "museum_name", "city_id", "city_name", "visitors", "population"]
    assert data["columns"] == expected_columns


def test_etl_run(client: TestClient):
    """Test ETL run endpoint."""
    response = client.post("/etl/run")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "museums" in data
    assert "cities" in data
    # year field should not be present anymore
    assert "year" not in data


def test_model_linear_empty(client: TestClient):
    """Test linear model endpoint returns empty metrics."""
    response = client.get("/model/linear")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "linear_regression"
    assert data["n_samples"] == 0
    assert data["r2"] is None
    assert data["mae"] is None
    assert data["rmse"] is None
    assert "notes" in data
