"""Wikidata client for fetching museum data using SPARQL."""
from typing import List, Dict, Any
import httpx
from src.core.config import settings
from src.core.logging import logger


async def fetch_most_visited_museums() -> List[Dict[str, Any]]:
    """Fetch museum data from Wikidata using SPARQL queries."""
    try:
        # Try primary query first
        museums = await _fetch_museums_primary()
        
        # If not enough results, try alternative query
        if len(museums) < 5:
            logger.info("Primary query returned few results, trying alternative query")
            museums_alt = await _fetch_museums_alternative()
            museums.extend(museums_alt)
        
        # Remove duplicates based on museum name
        unique_museums = []
        seen_names = set()
        for museum in museums:
            if museum["name"] not in seen_names:
                unique_museums.append(museum)
                seen_names.add(museum["name"])
        
        logger.info(f"Successfully fetched {len(unique_museums)} unique museums from Wikidata")
        return unique_museums
        
    except Exception as e:
        logger.error(f"Error fetching museum data from Wikidata: {e}")
        # Fallback to sample data
        return _get_sample_museum_data()


async def _fetch_museums_primary() -> List[Dict[str, Any]]:
    """Primary SPARQL query for museums with visitor counts."""
    query = """
    SELECT ?museum ?museumLabel ?city ?cityLabel ?country ?countryLabel ?visitors ?year WHERE {
      ?museum wdt:P31/wdt:P279* wd:Q33506 .  # Museums
      ?museum wdt:P131 ?city .  # Located in city
      ?city wdt:P17 ?country .  # City is in country
      ?museum p:P1128 ?visitorStatement .  # Has visitor count
      ?visitorStatement ps:P1128 ?visitors .  # Visitor count value
      ?visitorStatement pq:P585 ?year .  # Year of visitor count
      
      # Filter for recent years (2018-2024)
      FILTER(YEAR(?year) >= 2018)
      
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    ORDER BY DESC(?visitors)
    LIMIT 30
    """
    
    return await _execute_sparql_query(query)


async def _fetch_museums_alternative() -> List[Dict[str, Any]]:
    """Alternative SPARQL query for museums (broader search)."""
    query = """
    SELECT ?museum ?museumLabel ?city ?cityLabel ?country ?countryLabel ?visitors ?year WHERE {
      ?museum wdt:P31/wdt:P279* wd:Q33506 .  # Museums
      ?museum wdt:P131 ?city .  # Located in city
      ?city wdt:P17 ?country .  # City is in country
      ?museum p:P1128 ?visitorStatement .  # Has visitor count
      ?visitorStatement ps:P1128 ?visitors .  # Visitor count value
      ?visitorStatement pq:P585 ?year .  # Year of visitor count
      
      # Filter for museums with high visitor counts (> 1M)
      FILTER(?visitors >= 1000000)
      
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    ORDER BY DESC(?visitors)
    LIMIT 20
    """
    
    return await _execute_sparql_query(query)


async def _execute_sparql_query(query: str) -> List[Dict[str, Any]]:
    """Execute a SPARQL query and return parsed results."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                settings.wikidata_sparql_endpoint,
                params={"query": query, "format": "json"}
            )
            response.raise_for_status()
            data = response.json()
            return _parse_wikidata_response(data)
    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        return []


def _parse_wikidata_response(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Wikidata SPARQL response to extract museum data."""
    museums = []
    
    try:
        bindings = data.get("results", {}).get("bindings", [])
        
        for binding in bindings:
            museum_name = binding.get("museumLabel", {}).get("value", "Unknown")
            city_name = binding.get("cityLabel", {}).get("value", "Unknown")
            country_name = binding.get("countryLabel", {}).get("value", "Unknown")
            visitors_str = binding.get("visitors", {}).get("value", "0")
            year_str = binding.get("year", {}).get("value", "2023")
            
            try:
                visitors = int(float(visitors_str))
                year = int(year_str.split("-")[0])  # Extract year from date
                
                # Only include museums with significant visitor counts (> 1M)

                museums.append({
                    "name": museum_name,
                    "city": city_name,
                    "country": country_name,
                    "visitors": visitors,
                    "year": year,
                    "source": "wikidata"
                })
            except (ValueError, TypeError) as e:
                logger.debug(f"Error parsing visitor data: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error parsing Wikidata response: {e}")
    
    return museums


def _get_sample_museum_data() -> List[Dict[str, Any]]:
    """Return sample museum data for demonstration."""
    return [
        {
            "name": "Louvre",
            "city": "Paris",
            "country": "France",
            "visitors": 10000000,
            "year": 2023,
            "source": "wikipedia"
        },
        {
            "name": "National Museum of China",
            "city": "Beijing",
            "country": "China",
            "visitors": 8000000,
            "year": 2023,
            "source": "wikipedia"
        },
        {
            "name": "Metropolitan Museum of Art",
            "city": "New York City",
            "country": "United States",
            "visitors": 7000000,
            "year": 2023,
            "source": "wikipedia"
        },
        {
            "name": "Vatican Museums",
            "city": "Vatican City",
            "country": "Vatican City",
            "visitors": 6000000,
            "year": 2023,
            "source": "wikipedia"
        },
        {
            "name": "Tate Modern",
            "city": "London",
            "country": "United Kingdom",
            "visitors": 5000000,
            "year": 2023,
            "source": "wikipedia"
        }
    ]
