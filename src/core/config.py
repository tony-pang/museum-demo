import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    db_url: str = os.getenv("DB_URL", "postgresql://museum_user:museum_pass@postgres:5432/museum_db")
    wikipedia_api_endpoint: str = os.getenv("WIKIPEDIA_API_ENDPOINT", "https://en.wikipedia.org/w/api.php")
    wikidata_sparql_endpoint: str = os.getenv("WIKIDATA_SPARQL_ENDPOINT", "https://query.wikidata.org/sparql")


settings = Settings()
