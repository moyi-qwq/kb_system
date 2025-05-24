from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ES_HOST: str = "localhost"
    ES_PORT: int = 9200
    ES_USER: Optional[str] = None
    ES_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 