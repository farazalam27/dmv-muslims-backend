from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # Application settings
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    LOG_LEVEL: str = "INFO"
    DEFAULT_REGION: str = "dmv"
    
    # Database settings
    DATABASE_URL: str
    
    # Redis settings (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_KEY: str
    
    # API Keys
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    INSTAGRAM_API_KEY: Optional[str] = None
    TIKTOK_API_KEY: Optional[str] = None
    
    # Email settings
    RESEND_API_KEY: Optional[str] = None
    
    # Scraping settings
    SCRAPER_RUN_HOUR: int = 2
    ENABLE_INSTAGRAM_SCRAPING: bool = True
    ENABLE_TIKTOK_SCRAPING: bool = False
    
    # CORS settings
    FRONTEND_URL: str = "http://localhost:3000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v, values):
        if isinstance(v, str) and v:
            return [i.strip() for i in v.split(",")]
        return v or [values.get("FRONTEND_URL", "http://localhost:3000")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()