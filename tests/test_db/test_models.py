"""Tests for SQLAlchemy models."""
import pytest
from src.db.models import City, Museum, MuseumStat


def test_city_model():
    """Test City model creation."""
    city = City(
        wikidata_id="Q90",
        name="Paris",
        country="France",
        population=11000000,
        population_year=2023
    )
    assert city.name == "Paris"
    assert city.population == 11000000


def test_museum_model():
    """Test Museum model creation."""
    museum = Museum(
        wikidata_id="Q456",
        name="Louvre",
        city_id=1
    )
    assert museum.name == "Louvre"
    assert museum.wikidata_id == "Q456"
    assert museum.city_id == 1


def test_museum_stat_model():
    """Test MuseumStat model creation."""
    stat = MuseumStat(
        museum_id=1,
        year=2023,
        visitors=10000000
    )
    assert stat.year == 2023
    assert stat.visitors == 10000000
