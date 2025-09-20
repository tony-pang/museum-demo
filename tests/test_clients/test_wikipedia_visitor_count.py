"""Unit tests for visitor count extraction in Wikipedia client."""
import pytest
from src.clients.wikipedia import _extract_visitor_count


class TestExtractVisitorCount:
    """Test cases for _extract_visitor_count function."""

    def test_number_in_different_units(self):
        """Test numbers in different units."""
        assert _extract_visitor_count("2.5 million") == 2_500_000
        assert _extract_visitor_count("1,000 million") == 1_000_000_000
        assert _extract_visitor_count("1 million") == 1_000_000
        assert _extract_visitor_count("1.5 billion") == 1_500_000_000
        assert _extract_visitor_count("1.2 thousand") == 1_200
        assert _extract_visitor_count("1500000") == 1_500_000
        assert _extract_visitor_count("2500000.5") == 2_500_000
        """Test units with uppercase."""
        assert _extract_visitor_count("2.5 MILLION") == 2_500_000

        """Test units with extra whitespace."""
        assert _extract_visitor_count("2.5  million") == 2_500_000

        """Test very large numbers."""
        assert _extract_visitor_count("999.9 billion") == 999_900_000_000
        assert _extract_visitor_count("999999999") == 999_999_999


    def test_numbers_with_parentheses(self):
        """Test numbers with parentheses."""
        assert _extract_visitor_count("8,700,000 (2019)") == 8_700_000
        assert _extract_visitor_count("2.5 million (2020)") == 2_500_000
        assert _extract_visitor_count("1 billion (2021)") == 1_000_000_000
        assert _extract_visitor_count("8,700,000 (estimated)") == 8_700_000
        assert _extract_visitor_count("2.5 million (approx)") == 2_500_000

    def test_units_with_trailing_text(self):
        """Test units with additional text after."""
        assert _extract_visitor_count("2.5 million visitors") == 2_500_000
        assert _extract_visitor_count("1.5 billion people") == 1_500_000_000
        assert _extract_visitor_count("5 thousand annually") == 5_000

    def test_mixed_format_examples(self):
        """Test realistic mixed format examples."""
        assert _extract_visitor_count("8,700,000 (2023)") == 8_700_000
        assert _extract_visitor_count("2.5 million (2022)") == 2_500_000
        assert _extract_visitor_count("1.2 billion visitors") == 1_200_000_000
        assert _extract_visitor_count("500 thousand (est.)") == 500_000

    def test_edge_cases_zero(self):
        """Test edge cases with zero."""
        assert _extract_visitor_count("0") == 0
        assert _extract_visitor_count("0 million") == 0
        assert _extract_visitor_count("0.0 billion") == 0

    def test_invalid_inputs(self):
        """Test invalid inputs that should return 0."""
        assert _extract_visitor_count("") == 0
        assert _extract_visitor_count("abc") == 0
        assert _extract_visitor_count("million") == 0  # No number

    def test_malformed_numbers(self):
        """Test malformed numbers."""
        assert _extract_visitor_count("2.5.5 million") == 2  # Invalid decimal, takes first part
        assert _extract_visitor_count("2,,5 million") == 25000000  # Double comma ignored, becomes 25 million
        assert _extract_visitor_count("2.5 million million") == 2500000  # Double unit, takes first

    def test_unknown_units(self):
        """Test unknown units that are ignored."""
        assert _extract_visitor_count("2.5 trillion") == 2  # Unknown unit, returns raw number
        assert _extract_visitor_count("1.5 zillion") == 1  # Unknown unit, returns raw number
        assert _extract_visitor_count("5 hundred") == 5  # Unknown unit, returns raw number

    def test_negative_numbers(self):
        """Test negative numbers (currently not supported)."""
        assert _extract_visitor_count("-2.5 million") == 2500000  # Negative sign ignored

