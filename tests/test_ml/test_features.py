"""Tests for feature engineering."""
import pytest
import pandas as pd
from src.ml.features import load_features


def test_load_features():
    """Test loading features from database."""
    df = load_features()
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) > 0


def test_load_features_columns():
    """Test feature columns structure."""
    df = load_features()
    expected_columns = ["museum_id", "museum_name", "city_id", "city_name", "year", "visitors", "population"]
    assert df.columns.tolist() == expected_columns
