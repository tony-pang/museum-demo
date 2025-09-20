"""Wikipedia client for fetching museum data using the official Wikipedia API."""
from typing import List, Dict, Any
import httpx
import re
from bs4 import BeautifulSoup
from src.core.config import settings
from src.core.logging import logger


async def fetch_most_visited_museums() -> List[Dict[str, Any]]:
    """Fetch museum data from Wikipedia's list of most visited museums using the official API."""
    try:
        # Get the page content using Wikipedia API
        page_content = await _fetch_wikipedia_page_content()
        if not page_content:
            logger.error("Failed to fetch Wikipedia page content")
            return []

        # Parse the museum data from the page content
        museums = _parse_museum_data_from_content(page_content)

        logger.info(f"Successfully fetched {len(museums)} museums from Wikipedia API")
        return museums

    except Exception as e:
        logger.error(f"Error fetching museum data from Wikipedia API: {e}")
        return []


async def _fetch_wikipedia_page_content() -> str:
    """Fetch the Wikipedia page content using the official API."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Use Wikipedia API to get page content
            params = {
                'action': 'parse',
                'page': 'List_of_most-visited_museums',  # Correct page name with hyphen
                'format': 'json',
                'prop': 'text'
            }

            response = await client.get(settings.wikipedia_api_url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract the HTML content from the API response
            if 'parse' in data and 'text' in data['parse']:
                return data['parse']['text']['*']

            logger.error("No content found in Wikipedia API response")
            return ""

    except Exception as e:
        logger.error(f"Error fetching Wikipedia page via API: {e}")
        return ""

# TODO this is very specific to the wikipedia page, it should be more generic
# e.g. make a factory pattern for different data sources
def _parse_museum_data_from_content(html_content: str) -> List[Dict[str, Any]]:
    """Parse museum data from Wikipedia HTML content using Beautiful Soup."""
    museums = []

    try:
        # Parse HTML with Beautiful Soup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the table with museum data (look for wikitable class)
        table = soup.find('table', class_='wikitable')
        if not table:
            logger.warning("No wikitable found in Wikipedia content")
            return museums

        # Get all rows from tbody (skip thead)
        tbody = table.find('tbody')
        if not tbody:
            logger.warning("No tbody found in Wikipedia content")
            return museums

        for row in tbody.find_all('tr'):
            # Get all cells (only td elements, ignore th)
            cells = row.find_all('td')

            museum_data = _extract_museum_from_cells(cells)
            if museum_data:
                museums.append(museum_data)

    except Exception as e:
        logger.error(f"Error parsing museum data: {e}")

    return museums


def _is_valid_float(s: str) -> bool:
    """Check if a string can be converted to a valid float"""
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def _extract_visitor_count(visitor_cell: str) -> int:
    """Extract visitor count from a cell, handling various formats like '2.5 million', '8,700,000', etc."""
    visitors = 0

    # Handle None or non-string input
    if visitor_cell is None:
        return 0

    # Convert to string if not already
    visitor_cell = str(visitor_cell)

    # Remove (year) from visitor_cell, e.g., "8,700,000 (2019)" -> "8,700,000"
    # This regex removes anything inside parentheses, including the parentheses themselves.
    visitor_cell = re.sub(r'\(.*?\)', '', visitor_cell)

    # Try to find patterns like "2.5 million", "1 billion", etc.
    text_number_pattern = r'([\d,]+\.?\d*)\s*([a-zA-Z]+)?'
    text_match = re.search(text_number_pattern, visitor_cell, re.IGNORECASE)

    if not text_match:
        logger.debug(f"No text match found in visitor_cell: {visitor_cell}")
        return 0

    number_part = text_match.group(1).replace(',', '')
    unit_part = text_match.group(2)  # Could be None or any text

    # Check if the number part is a valid float (like Go's strconv.ParseFloat)
    if not _is_valid_float(number_part):
        logger.error(f"Invalid number format: '{number_part}'")
        return 0

    visitors = float(number_part)

    if visitors < 0:
        logger.debug(f"Negative number found in visitor_cell: {visitor_cell}")
        return 0

    # Apply multiplication based on unit (or no multiplication if no unit)
    if not unit_part:
        return int(visitors)

    unit = unit_part.strip().lower()
    if unit == 'thousand':
        return int(visitors * 1_000)
    if unit == 'million':
        return int(visitors * 1_000_000)
    if unit == 'billion':
        return int(visitors * 1_000_000_000)
    # Could add more units here as needed

    logger.warning(f"Unknown unit: {unit}, using raw number")
    return int(visitors)

def clean_html(text: str) -> str:
    """Remove HTML tags, reference numbers, flag images, and clean up whitespace and quotes."""
    if not text:
        return ""

    # Parse with Beautiful Soup to handle HTML properly
    soup = BeautifulSoup(str(text), 'html.parser')

    # Remove reference numbers like [1], [2]
    for ref in soup.find_all('sup', class_='reference'):
        ref.decompose()

    # Remove flag images and other images
    for img in soup.find_all('img'):
        img.decompose()

    # Get clean text
    text = soup.get_text()

    # Remove reference numbers like [1], [2] (fallback for any remaining)
    text = re.sub(r'\[\d+\]', '', text)

    # Remove markdown-style flag images like ![](//upload.wikimedia.org/...)
    text = re.sub(r'!\[.*?\]\([^)]+\)', '', text)

    # Clean up whitespace and quotes
    text = text.replace('"', '').strip()
    return text


def _extract_museum_from_cells(cells) -> Dict[str, Any]:
    """Extract museum data from Beautiful Soup table cells."""
    if len(cells) < 4:  # Need at least museum name, visitors, city and country
        logger.warning(f"Missing essential data: only {len(cells)} cells provided, need 4")
        return None

    try:
        # Extract museum name (first cell)
        museum_name = clean_html(cells[0].get_text())

        # Extract visitor count (second cell)
        visitor_cell = clean_html(cells[1].get_text())

        # Look for year in parentheses (e.g., "1,324,000 (2023)")
        year_match = re.search(r'\((\d{4})\)', visitor_cell)
        year = int(year_match.group(1)) if year_match else 0

        # Extract visitor count from the cell
        visitors = _extract_visitor_count(visitor_cell)

        if visitors < 2_000_000:
            logger.warning(f"Visitor count is less than 2,000,000: {visitors}")
            return None

        # Extract city (3rd column) and country (4th column)
        city = clean_html(cells[2].get_text()).strip()
        country = clean_html(cells[3].get_text()).strip()

        # Only return if we have essential data
        if not (museum_name and city and country):
            logger.warning(f"Missing essential data: name='{museum_name}', city='{city}', country='{country}'")
            return None

        return {
            "name": museum_name,
            "city": city,
            "country": country,
            "visitors": visitors,
            "year": year,
            "source": "wikipedia_api"
        }

    except (AttributeError, ValueError, TypeError) as e:
        logger.debug(f"Error extracting museum from cells: {e}")
        return None
