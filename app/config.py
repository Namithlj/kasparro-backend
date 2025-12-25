from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    API_KEY: Optional[str] = None
    DEFAULT_PAGE_SIZE: int = 20

    # In Pydantic v2, we use model_config instead of class Config
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()