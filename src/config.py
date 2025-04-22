import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Optional

# 加载环境变量
load_dotenv()

# Elasticsearch配置
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "elasticsearch")
ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))

# 构建Elasticsearch连接URL
ELASTICSEARCH_URL = f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}"

class Settings(BaseSettings):
    ES_HOST: str = ELASTICSEARCH_HOST
    ES_PORT: int = ELASTICSEARCH_PORT
    ES_USER: Optional[str] = None
    ES_PASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings() 