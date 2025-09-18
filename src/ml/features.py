"""Feature engineering for museum attendance data."""
from typing import Tuple
import pandas as pd
from sqlalchemy.orm import Session
from src.db.session import SessionLocal
from src.db.models import Museum, City, MuseumStat


def load_features() -> Tuple[pd.DataFrame, list[str]]:
    """Load features from the database by joining museums, cities, and stats."""
    columns = ["museum_id", "museum_name", "city_id", "city_name", "year", "visitors", "population"]
    
    try:
        with SessionLocal() as db:
            # Query to join all tables
            query = db.query(
                Museum.id.label('museum_id'),
                Museum.name.label('museum_name'),
                City.id.label('city_id'),
                City.name.label('city_name'),
                MuseumStat.year,
                MuseumStat.visitors,
                City.population
            ).join(
                City, Museum.city_id == City.id
            ).join(
                MuseumStat, Museum.id == MuseumStat.museum_id
            )
            
            # Execute query and convert to DataFrame
            results = query.all()
            
            if not results:
                return pd.DataFrame(columns=columns), columns
            
            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append({
                    'museum_id': row.museum_id,
                    'museum_name': row.museum_name,
                    'city_id': row.city_id,
                    'city_name': row.city_name,
                    'year': row.year,
                    'visitors': row.visitors,
                    'population': row.population
                })
            
            df = pd.DataFrame(data)
            return df, columns
            
    except Exception as e:
        print(f"Error loading features: {e}")
        return pd.DataFrame(columns=columns), columns
