from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CACE-AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "caceai"
    
    SECRET_KEY: str = "caceai-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # LLM provider
    LLM_PROVIDER: str = "gemini"  # openai | gemini | deepseek
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 800
    
    # Agent settings
    MAX_CONTEXT_NODES: int = 15
    MIN_RELEVANCE: float = 0.3
    SECURITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
