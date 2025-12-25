from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    API_KEY: Optional[str] = None
    DEFAULT_PAGE_SIZE: int = 20
    # Added this to fix the AttributeError in etl.py
    ETL_INTERVAL_SECONDS: int = 3600  

    # Pydantic v2 configuration
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()