"""Unit tests for museum data extraction from HTML table cells."""
import pytest
from bs4 import BeautifulSoup
from src.clients.wikipedia import _extract_museum_from_cells


class TestExtractMuseumFromCells:
    """Test cases for _extract_museum_from_cells function."""

    def test_valid_museum_data(self):
        """Test extraction with valid museum data."""
        # Create Beautiful Soup elements with proper HTML content
        soup = BeautifulSoup("", 'html.parser')
        cells = [
            BeautifulSoup("<td>Louvre</td>", 'html.parser').find('td'),  # Museum name
            BeautifulSoup("<td>8,700,000 (2024)</td>", 'html.parser').find('td'),  # Visitors
            BeautifulSoup("<td>Paris</td>", 'html.parser').find('td'),  # City
            BeautifulSoup("<td>France</td>", 'html.parser').find('td')  # Country
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is not None
        assert result["name"] == "Louvre"
        assert result["city"] == "Paris"
        assert result["country"] == "France"
        assert result["source"] == "wikipedia_api"

    def test_museum_with_html_tags_and_references(self):
        """Test extraction with HTML tags and reference numbers."""
        # Create Beautiful Soup elements with HTML content
        cells = [
            BeautifulSoup("<td>[Louvre](/wiki/Louvre \"Louvre\")</td>", 'html.parser').find('td'),  # Museum name with markdown link
            BeautifulSoup("<td>8,700,000 (2024)[1]</td>", 'html.parser').find('td'),  # Visitors with reference
            BeautifulSoup("<td>[Paris](/wiki/Paris \"Paris\")</td>", 'html.parser').find('td'),  # City with markdown link
            BeautifulSoup("<td>![](//upload.wikimedia.org/flag.svg) [France](/wiki/France \"France\")</td>", 'html.parser').find('td')  # Country with flag
        ]

        result = _extract_museum_from_cells(cells)

        assert result is not None
        assert result["name"] == "[Louvre](/wiki/Louvre Louvre)"  # Markdown links not removed
        assert result["city"] == "[Paris](/wiki/Paris Paris)"  # Markdown links not removed
        assert result["country"] == "[France](/wiki/France France)"  # Flag removed, markdown link remains

    def test_insufficient_cells(self):
        """Test with insufficient number of cells."""
        cells = [
            BeautifulSoup("<td>Louvre</td>", 'html.parser').find('td'),  # Museum name
            BeautifulSoup("<td>8,700,000</td>", 'html.parser').find('td'),  # Visitors
            BeautifulSoup("<td>Paris</td>", 'html.parser').find('td')  # City only, no country
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is None

    def test_empty_museum_name(self):
        """Test with empty museum name."""
        cells = [
            BeautifulSoup("<td></td>", 'html.parser').find('td'),  # Empty museum name
            BeautifulSoup("<td>8,700,000</td>", 'html.parser').find('td'),
            BeautifulSoup("<td>Paris</td>", 'html.parser').find('td'),
            BeautifulSoup("<td>France</td>", 'html.parser').find('td')
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is None

    def test_empty_city(self):
        """Test with empty city."""
        cells = [
            BeautifulSoup("<td>Louvre</td>", 'html.parser').find('td'),
            BeautifulSoup("<td>8,700,000</td>", 'html.parser').find('td'),
            BeautifulSoup("<td></td>", 'html.parser').find('td'),  # Empty city
            BeautifulSoup("<td>France</td>", 'html.parser').find('td')
        ]
        
        result = _extract_museum_from_cells(cells)
        
        assert result is None

    def test_complex_html_cleaning(self):
        """Test complex HTML cleaning scenarios."""
        cells = [
            BeautifulSoup("<td><a href='/wiki/Metropolitan_Museum_of_Art'>Metropolitan Museum of Art</a></td>", 'html.parser').find('td'),
            BeautifulSoup("<td>5,727,258 (2024) [6]</td>", 'html.parser').find('td'),
            BeautifulSoup("<td><span>New York City</span></td>", 'html.parser').find('td'),
            BeautifulSoup("<td>![](//upload.wikimedia.org/flag.svg) <a href='/wiki/United_States'>United States</a></td>", 'html.parser').find('td')
        ]

        result = _extract_museum_from_cells(cells)

        assert result is not None
        assert result["name"] == "Metropolitan Museum of Art"
        assert result["city"] == "New York City"
        assert result["country"] == "United States"
