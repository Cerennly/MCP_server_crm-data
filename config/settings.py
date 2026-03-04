from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./crm.db"
    MASTER_API_KEY: str = "crm_master_changeme"
    API_KEY_PREFIX: str = "crm_"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    MCP_SERVER_NAME: str = "CRM-MCP-Server"
    MCP_SERVER_VERSION: str = "2.0.0"
    HF_DATASET: str = "adityaswami89/Salesdata"
    HF_MAX_CUSTOMERS: int = 50
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
