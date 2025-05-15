import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "CivicLens"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "https://civiclens.yourdomain.com"]
    
    # DeepSeek API settings
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")    
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"

    # OpenAI API settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # OpenAI Model settings
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Cache settings
    CACHE_EXPIRY: int = 3600  # Cache responses for 1 hour
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Default response settings
    SIMPLIFIED_RESPONSE_TOKENS: int = 300
    DETAILED_RESPONSE_TOKENS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()