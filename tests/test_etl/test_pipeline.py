"""Tests for ETL pipeline."""
import pytest
from src.etl.pipeline import run_etl


def test_run_etl_default():
    """Test ETL pipeline with default parameters."""
    result = run_etl()
    assert result["status"] == "ok"
    assert "year" in result
    assert "museums" in result
    assert "cities" in result


def test_run_etl_with_year():
    """Test ETL pipeline with specific year."""
    result = run_etl(year=2023)
    assert result["status"] == "ok"
    assert result["year"] == 2023
