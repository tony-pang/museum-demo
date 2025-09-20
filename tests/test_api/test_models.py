"""Tests for Pydantic models."""
import pytest
from src.api.main import Health


def test_health_model():
    """Test Health model validation."""
    health = Health(status="ok")
    assert health.status == "ok"

    # Test with different status
    health = Health(status="error")
    assert health.status == "error"


def test_health_model_validation():
    """Test Health model validation errors."""
    with pytest.raises(ValueError):
        Health()  # Missing required field
