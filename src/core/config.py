import os
from pydantic import BaseModel

# TODO use dynaconf instead of os.getenv
class Settings(BaseModel):
    db_url: str = os.getenv("DB_URL", "postgresql://museum_user:museum_pass@postgres:5432/museum_db")
    wikipedia_api_url: str = os.getenv("WIKIPEDIA_API_URL", "https://en.wikipedia.org/w/api.php")
    wikidata_endpoint: str = os.getenv("WIKIDATA_URL", "https://query.wikidata.org/sparql")


settings = Settings()
