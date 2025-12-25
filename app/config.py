from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    API_KEY: Optional[str] = None # Your internal key for /run-etl
    
    # External API Keys
    COINGECKO_API_KEY: Optional[str] = None
    COINPAPRIKA_API_KEY: Optional[str] = None
    
    DEFAULT_PAGE_SIZE: int = 20
    ETL_INTERVAL_SECONDS: int = 3600

    model_config = ConfigDict(env_file=".env", extra="ignore")
settings = Settings()