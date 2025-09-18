"""Tests for ML models."""
import pytest
import numpy as np
from src.ml.model import fit_linear_regression


def test_fit_linear_regression_empty():
    """Test linear regression with empty data."""
    X = np.array([]).reshape(0, 1)
    y = np.array([])
    result = fit_linear_regression(X, y)
    assert result["n_samples"] == 0
    assert result["r2"] is None
    assert result["mae"] is None
    assert result["rmse"] is None


def test_fit_linear_regression_simple():
    """Test linear regression with simple data."""
    X = np.array([[1], [2], [3], [4]])
    y = np.array([2, 4, 6, 8])
    result = fit_linear_regression(X, y)
    assert result["n_samples"] == 4
    assert result["r2"] == 1.0  # Perfect fit
    assert result["mae"] == 0.0
    assert result["rmse"] == 0.0
