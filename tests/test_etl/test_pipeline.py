"""Tests for ETL pipeline."""
import pytest
from unittest.mock import patch, AsyncMock
from src.etl.pipeline import run_etl


@patch('src.etl.pipeline.Base.metadata.create_all')
@patch('src.etl.pipeline.asyncio.run')
def test_run_etl(mock_asyncio_run, mock_create_all):
    """Test ETL pipeline."""
    # Mock the async ETL function to return a successful result
    mock_asyncio_run.return_value = {
        "status": "ok",
        "museums": 5,
        "cities": 3
    }

    result = run_etl()
    assert result["status"] == "ok"
    assert "museums" in result
    assert "cities" in result
    # year field should not be present anymore
    assert "year" not in result
