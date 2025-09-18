"""Tests for database session."""
import pytest
from src.db.session import engine, SessionLocal


def test_engine_creation():
    """Test database engine creation."""
    assert engine is not None
    assert str(engine.url).startswith("postgresql")


def test_session_creation():
    """Test database session creation."""
    session = SessionLocal()
    assert session is not None
    session.close()
