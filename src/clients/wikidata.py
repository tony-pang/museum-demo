"""Wikidata client for fetching city population data."""
from typing import Dict, Any, Optional
import httpx
from src.core.config import settings
from src.core.logging import logger


async def fetch_city_population(wikidata_qid: str) -> Dict[str, Any]:
    """Fetch city population from Wikidata using SPARQL."""
    try:
        query = f"""
        SELECT ?population ?pointInTime ?cityName WHERE {{
          wd:{wikidata_qid} rdfs:label ?cityName .
          FILTER(LANG(?cityName) = "en")
          wd:{wikidata_qid} p:P1082 ?populationStatement .
          ?populationStatement ps:P1082 ?population ;
                             pq:P585 ?pointInTime .
        }} ORDER BY DESC(?pointInTime)
        LIMIT 1
        """
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                settings.wikidata_sparql_endpoint, 
                params={"query": query, "format": "json"}
            )
            resp.raise_for_status()
            data = resp.json()
            
            bindings = data.get("results", {}).get("bindings", [])
            if bindings:
                result = bindings[0]
                return {
                    "population": int(result.get("population", {}).get("value", 0)),
                    "year": result.get("pointInTime", {}).get("value", "").split("-")[0] if result.get("pointInTime") else None,
                    "city_name": result.get("cityName", {}).get("value", ""),
                    "wikidata_id": wikidata_qid
                }
            
    except Exception as e:
        logger.error(f"Error fetching population for {wikidata_qid}: {e}")
    
    return {}


async def search_city_by_name(city_name: str, country: str = None) -> Optional[str]:
    """Search for a city's Wikidata QID by name."""
    try:
        query = f"""
        SELECT ?city ?cityLabel WHERE {{
          ?city wdt:P31/wdt:P279* wd:Q515 .
          ?city rdfs:label ?cityLabel .
          FILTER(CONTAINS(LCASE(?cityLabel), LCASE("{city_name}")))
        }}
        LIMIT 5
        """
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                settings.wikidata_sparql_endpoint,
                params={"query": query, "format": "json"}
            )
            resp.raise_for_status()
            data = resp.json()
            
            bindings = data.get("results", {}).get("bindings", [])
            if bindings:
                # Return the first match
                city_uri = bindings[0].get("city", {}).get("value", "")
                return city_uri.split("/")[-1]  # Extract QID from URI
            
    except Exception as e:
        logger.error(f"Error searching for city {city_name}: {e}")
    
    return None


def get_sample_city_populations() -> Dict[str, Dict[str, Any]]:
    """Return sample city population data for demonstration."""
    return {
        "Paris": {
            "population": 11000000,
            "year": 2023,
            "city_name": "Paris",
            "wikidata_id": "Q90"
        },
        "Beijing": {
            "population": 22000000,
            "year": 2023,
            "city_name": "Beijing",
            "wikidata_id": "Q956"
        },
        "New York City": {
            "population": 19000000,
            "year": 2023,
            "city_name": "New York City",
            "wikidata_id": "Q60"
        },
        "Vatican City": {
            "population": 800,
            "year": 2023,
            "city_name": "Vatican City",
            "wikidata_id": "Q237"
        },
        "London": {
            "population": 9000000,
            "year": 2023,
            "city_name": "London",
            "wikidata_id": "Q84"
        }
    }
