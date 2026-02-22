"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # API metadata
    app_name: str = "Financial Consolidation Engine"
    app_version: str = "0.1.0"
    app_description: str = "Mini FP&A consolidation engine for learning and demonstration purposes."
    
    # API configuration
    api_v1_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
