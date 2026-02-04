"""
Configuration management for the application
"""
import os
from pathlib import Path
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    webpagetest_api_key: str = os.getenv("WEBPAGETEST_API_KEY", "")
    gtmetrix_api_key: str = os.getenv("GTMETRIX_API_KEY", "")
    gtmetrix_api_username: str = os.getenv("GTMETRIX_API_USERNAME", "")

    # Server Configuration
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Storage
    reports_dir: Path = Path(os.getenv("REPORTS_DIR", "./reports"))
    screenshots_dir: Path = Path(os.getenv("SCREENSHOTS_DIR", "./screenshots"))

    # LangGraph Configuration
    langchain_tracing_v2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
