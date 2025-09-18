"""ETL pipeline for museum and city data."""
import asyncio
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.core.logging import logger
from src.db.session import SessionLocal, engine
from src.db.models import Base, City, Museum, MuseumStat
from src.clients.wikipedia import fetch_most_visited_museums
from src.clients.wikidata import fetch_city_population, get_sample_city_populations


def run_etl(year: int | None = None) -> dict:
    """Run the complete ETL pipeline."""
    logger.info(f"Starting ETL pipeline for year={year}")
    
    try:
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # Run async ETL
        result = asyncio.run(_run_async_etl(year))
        
        logger.info(f"ETL completed successfully: {result}")
        return result
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        return {"status": "error", "error": str(e), "year": year, "museums": 0, "cities": 0}


async def _run_async_etl(year: int | None = None) -> dict:
    """Run the async ETL operations."""
    museums_processed = 0
    cities_processed = 0
    
    # Fetch museum data from Wikipedia
    logger.info("Fetching museum data from Wikipedia...")
    museums_data = await fetch_most_visited_museums()
    
    if not museums_data:
        logger.warning("No museum data fetched, using sample data")
        museums_data = _get_sample_museum_data()
    
    # Get sample city populations (in production, you'd fetch from Wikidata)
    city_populations = get_sample_city_populations()
    
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
        "year": year or 2023,
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
    
    # Get population data
    population_data = city_populations.get(city_name, {})
    
    # Create new city
    city = City(
        name=city_name,
        country=country,
        population=population_data.get("population"),
        population_year=int(population_data.get("year", 2023)),
        wikidata_id=population_data.get("wikidata_id"),
        source="wikidata"
    )
    
    db.add(city)
    db.flush()  # Get the ID
    return city


def _create_museum(db: Session, museum_data: Dict[str, Any], city: City | None) -> Museum | None:
    """Create a museum record."""
    try:
        museum = Museum(
            name=museum_data.get("name", "Unknown"),
            city_id=city.id if city else None,
            wikidata_id=None,  # Could be fetched from Wikidata
            source=museum_data.get("source", "wikipedia")
        )
        
        db.add(museum)
        db.flush()  # Get the ID
        return museum
        
    except Exception as e:
        logger.error(f"Error creating museum: {e}")
        return None


def _create_museum_stats(db: Session, museum: Museum, museum_data: Dict[str, Any]) -> None:
    """Create museum statistics record."""
    try:
        stat = MuseumStat(
            museum_id=museum.id,
            year=int(museum_data.get("year", 2023)),
            visitors=int(museum_data.get("visitors", 0)),
            source=museum_data.get("source", "wikipedia")
        )
        
        db.add(stat)
        
    except Exception as e:
        logger.error(f"Error creating museum stats: {e}")


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
