"""ETL pipeline for museum and city data."""
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.core.logging import logger
from src.db.session import SessionLocal, engine
from src.db.models import Base, City, Museum, MuseumStat
from src.clients.wikipedia import fetch_most_visited_museums
from src.clients.wikidata import fetch_city_population, search_city_by_name


def run_etl() -> dict:
    """Run the complete ETL pipeline."""
    logger.info("Starting ETL pipeline")
    
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # Run async ETL
        result = asyncio.run(_run_async_etl())
        
        logger.info(f"ETL completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        return {"status": "error", "error": str(e), "museums": 0, "cities": 0}


async def _run_async_etl() -> dict:
    """Run the async ETL operations."""
    museums_processed = 0
    cities_processed = 0
    
    # Fetch museum data from Wikipedia
    logger.info("Fetching museum data from Wikipedia...")
    museums_data = await fetch_most_visited_museums()
    
    if not museums_data:
        logger.warning("No museum data fetched from Wikidata")
        return {
            "status": "error",
            "museums": 0,
            "cities": 0,
            "error": "No museum data available from Wikidata"
        }
    
    # Get city populations from Wikidata
    city_populations = await _fetch_city_populations_for_museums(museums_data)
    
    # Process data in database
    with SessionLocal() as db:
        for museum_data in museums_data:
            try:
                # Create or get city
                city = _get_or_create_city(db, museum_data, city_populations)
                if city:
                    cities_processed += 1
                
                # Create museum
                museum = _create_museum(db, museum_data, city)
                if museum:
                    museums_processed += 1
                    
                    # Create museum stats
                    _create_museum_stats(db, museum, museum_data)
                
            except Exception as e:
                logger.error(f"Error processing museum {museum_data.get('name', 'Unknown')}: {e}")
                continue
        
        db.commit()
    
    return {
        "status": "ok",
        "museums": museums_processed,
        "cities": cities_processed
    }


def _get_or_create_city(db: Session, museum_data: Dict[str, Any], city_populations: Dict[str, Dict[str, Any]]) -> City | None:
    """Get or create a city record."""
    city_name = museum_data.get("city", "Unknown")
    country = museum_data.get("country", "Unknown")
    
    # Check if city already exists
    existing_city = db.query(City).filter(
        City.name == city_name,
        City.country == country
    ).first()
    
    if existing_city:
        return existing_city
    
    # Get population data - try exact match first, then partial match
    population_data = city_populations.get(city_name, {})
    if not population_data:
        # Try partial matching for city names
        for key, data in city_populations.items():
            if city_name.lower() in key.lower() or key.lower() in city_name.lower():
                population_data = data
                logger.info(f"Matched city '{city_name}' with '{key}' for population data")
                break
    
    # Create new city with proper defaults
    current_time = datetime.now().isoformat()
    city = City(
        name=city_name,
        country=country,
        population=population_data.get("population", 0) if population_data else 0,
        population_year=int(population_data.get("year", 2023)) if population_data else 2023,
        wikidata_id=population_data.get("wikidata_id") if population_data else None,
        last_updated=current_time
    )
    
    db.add(city)
    db.flush()  # Get the ID
    logger.info(f"Created city: {city_name}, {country}, population: {city.population}")
    return city


def _create_museum(db: Session, museum_data: Dict[str, Any], city: City | None) -> Museum | None:
    """Create a museum record."""
    try:
        museum_name = museum_data.get("name", "Unknown")
        city_id = city.id if city else None
        
        # Check if museum already exists
        existing_museum = db.query(Museum).filter(
            Museum.name == museum_name,
            Museum.city_id == city_id
        ).first()
        
        if existing_museum:
            logger.debug(f"Museum {museum_name} already exists, skipping")
            return existing_museum
        
        current_time = datetime.now().isoformat()
        museum = Museum(
            name=museum_name,
            city_id=city_id,
            wikidata_id=None,  # Could be fetched from Wikidata
            last_updated=current_time
        )
        
        db.add(museum)
        db.flush()  # Get the ID
        logger.info(f"Created museum: {museum.name} in city_id: {museum.city_id}")
        return museum
        
    except Exception as e:
        logger.error(f"Error creating museum: {e}")
        db.rollback()  # Rollback on error
        return None


def _create_museum_stats(db: Session, museum: Museum, museum_data: Dict[str, Any]) -> None:
    """Create museum statistics record."""
    try:        
        # Check if stats already exist for this museum
        existing_stat = db.query(MuseumStat).filter(
            MuseumStat.museum_id == museum.id
        ).first()
        
        if existing_stat:
            logger.debug(f"Museum stats for {museum.name} already exist, skipping")
            return
        
        current_time = datetime.now().isoformat()
        stat = MuseumStat(
            museum_id=museum.id,
            year=int(museum_data.get("year", 0)),
            visitors=int(museum_data.get("visitors", 0)),
            last_updated=current_time
        )
        
        db.add(stat)
        logger.info(f"Created museum stats: {museum.name} - {stat.visitors} visitors in {stat.year}")
        
    except Exception as e:
        logger.error(f"Error creating museum stats: {e}")
        db.rollback()  # Rollback on error


async def _fetch_city_populations_for_museums(museums_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Fetch city population data for all unique cities in museum data."""
    city_populations = {}
    unique_cities = set()
    
    # Extract unique cities
    for museum in museums_data:
        city_name = museum.get("city", "") 
        country = museum.get("country", "")
        if not city_name or not country:
            # According to the Wikipedia page, the city and country are always present. 
            # Since this is the only source, I assume that the data is missing and skip the museum.
            logger.warning(f"City or country is missing for museum: {museum}")
            continue

        unique_cities.add((city_name, country))
    
    # First, check database for existing cities
    cities_to_fetch = []
    for city_name, country in unique_cities:
        with SessionLocal() as db:
            city = db.query(City).filter(City.name == city_name, City.country == country).first()
            if not city:
                cities_to_fetch.append((city_name, country))
                continue

            city_populations[city_name] = {
                "population": city.population,
                "year": city.population_year,
                "wikidata_id": city.wikidata_id
            }
            logger.info(f"Using cached population data for {city_name}: {city.population}")
    
    # Fetch population data for remaining cities in parallel (batched to avoid rate limits)
    if not cities_to_fetch:
        logger.info("No cities to fetch population data for")
        return city_populations

    logger.info(f"Fetching population data for {len(cities_to_fetch)} cities in parallel (batched)...")
    
    async def fetch_single_city_population(city_name: str, country: str) -> tuple[str, dict]:
        """Fetch population data for a single city."""
        try:
            logger.info(f"Fetching population data for city: {city_name}, {country}")
            
            # Search for the city's Wikidata QID
            qid = await search_city_by_name(city_name, country)
            
            if not qid:
                logger.warning(f"Could not find Wikidata QID for city: {city_name}, {country}")
                return city_name, {}
            # Fetch population data using the QID
            population_data = await fetch_city_population(qid)
            if not population_data:
                logger.warning(f"No population data found for {city_name} (QID: {qid})")
                return city_name, {}
        
            logger.info(f"Found population data for {city_name}: {population_data.get('population', 0)}")
            return city_name, population_data
        except Exception as e:
            logger.error(f"Error fetching population for {city_name}: {e}")
            return city_name, {}
    
    # Process cities in batches of 10 to avoid overwhelming the API
    # TODO: make this configurable
    batch_size = 10
    all_results = []
    
    for i in range(0, len(cities_to_fetch), batch_size):
        batch = cities_to_fetch[i:i + batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}/{(len(cities_to_fetch) + batch_size - 1)//batch_size} ({len(batch)} cities)")
        
        # Use asyncio.gather to fetch cities in this batch in parallel
        batch_results = await asyncio.gather(
            *[fetch_single_city_population(city_name, country) for city_name, country in batch],
            return_exceptions=True
        )
        
        all_results.extend(batch_results)
        
        # Small delay between batches to be respectful to the API
        if i + batch_size < len(cities_to_fetch):
            await asyncio.sleep(0.5)
    
    # Process all results
    for result in all_results:
        if isinstance(result, Exception):
            logger.error(f"Unexpected error in parallel fetch: {result}")
            continue
        city_name, population_data = result
        city_populations[city_name] = population_data
    
    return city_populations
