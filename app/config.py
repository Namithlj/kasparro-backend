from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/dev.db"
    API_KEY: Optional[str] = None
    ETL_INTERVAL_SECONDS: int = 60
    DEFAULT_PAGE_SIZE: int = 25

    class Config:
        env_file = ".env"


settings = Settings()
