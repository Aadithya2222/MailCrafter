"""
Configuration management using environment variables.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    GEMINI_API_KEY: str
    
    # Gmail SMTP Configuration
    GMAIL_USER: str
    GMAIL_APP_PASSWORD: str
    
    # Whisper Configuration (optional)
    WHISPER_MODEL: str = "base"
    USE_WHISPER_STUB: bool = False  # Set to True for testing without Whisper
    
    # CORS
    # Keep as string to avoid dotenv JSON parsing issues for List[str] in pydantic-settings.
    # Format: comma-separated origins.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Security
    MAX_AUDIO_SIZE_MB: int = 10
    MAX_AUDIO_DURATION_SECONDS: int = 300  # 5 minutes
    
    # Database (for contacts only, not email content)
    DATABASE_URL: str = "sqlite:///./backend/data/contacts.db"

    @property
    def cors_origins_list(self) -> List[str]:
        parts = [p.strip() for p in (self.CORS_ORIGINS or "").split(",")]
        return [p for p in parts if p]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
