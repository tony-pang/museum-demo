"""Unit tests for museum data extraction from HTML table cells."""
import pytest
from src.clients.wikipedia import _extract_museum_from_cells


class TestExtractMuseumFromCells:
    """Test cases for _extract_museum_from_cells function."""

    def test_valid_museum_data(self):
        """Test extraction with valid museum data."""
        cells = [
            "Louvre",  # Museum name
            "8,700,000 (2024)",  # Visitors
            "Paris",  # City
            "France"  # Country
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is not None
        assert result["name"] == "Louvre"
        assert result["city"] == "Paris"
        assert result["country"] == "France"
        assert result["source"] == "wikipedia_api"

    def test_museum_with_html_tags_and_references(self):
        """Test extraction with HTML tags and reference numbers."""
        cells = [
            "[Louvre](/wiki/Louvre \"Louvre\")",  # Museum name with markdown link
            "8,700,000 (2024)[1]",  # Visitors with reference
            "[Paris](/wiki/Paris \"Paris\")",  # City with markdown link
            "![](//upload.wikimedia.org/flag.svg) [France](/wiki/France \"France\")"  # Country with flag
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is not None
        assert result["name"] == "[Louvre](/wiki/Louvre Louvre)"  # Markdown links not removed
        assert result["city"] == "[Paris](/wiki/Paris Paris)"  # Markdown links not removed
        assert result["country"] == "[France](/wiki/France France)"  # Flag removed, markdown link remains

    def test_insufficient_cells(self):
        """Test with insufficient number of cells."""
        cells = [
            "Louvre",  # Museum name
            "8,700,000",  # Visitors
            "Paris"  # City only, no country
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is None

    def test_empty_museum_name(self):
        """Test with empty museum name."""
        cells = [
            "",  # Empty museum name
            "8,700,000",
            "Paris",
            "France"
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is None

    def test_empty_city(self):
        """Test with empty city."""
        cells = [
            "Louvre",
            "8,700,000",
            "",  # Empty city
            "France"
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is None

    def test_complex_html_cleaning(self):
        """Test complex HTML cleaning scenarios."""
        cells = [
            "<a href='/wiki/Metropolitan_Museum_of_Art'>Metropolitan Museum of Art</a>",
            "5,727,258 (2024) [6]",
            "<span>New York City</span>",
            "![](//upload.wikimedia.org/flag.svg) <a href='/wiki/United_States'>United States</a>"
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is not None
        assert result["name"] == "Metropolitan Museum of Art"
        assert result["city"] == "New York City"
        assert result["country"] == "United States"
