"""Feature engineering for museum attendance data."""
import pandas as pd
import numpy as np
from src.db.session import SessionLocal
from src.db.models import Museum, City, MuseumStat


def load_features() -> pd.DataFrame:
    """Load features from the database by joining museums, cities, and stats."""
    try:
        with SessionLocal() as db:
            # Query to join all tables
            query = db.query(
                Museum.id.label('museum_id'),
                Museum.name.label('museum_name'),
                City.id.label('city_id'),
                City.name.label('city_name'),
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
                return pd.DataFrame(columns=["museum_id", "museum_name", "city_id", "city_name", "visitors", "population"])

            # Convert to list of dictionaries
            data = []
            for row in results:
                data.append({
                    'museum_id': row.museum_id,
                    'museum_name': row.museum_name,
                    'city_id': row.city_id,
                    'city_name': row.city_name,
                    'visitors': row.visitors,
                    'population': row.population
                })

            df = pd.DataFrame(data)

            # Ensure numeric columns are properly typed
            if 'population' in df.columns:
                df['population'] = pd.to_numeric(df['population'], errors='coerce').fillna(0).astype(int)
            if 'visitors' in df.columns:
                df['visitors'] = pd.to_numeric(df['visitors'], errors='coerce').fillna(0).astype(int)

            return df

    except Exception as e:
        print(f"Error loading features: {e}")
        return pd.DataFrame(columns=["museum_id", "museum_name", "city_id", "city_name", "visitors", "population"])
