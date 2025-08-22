from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    groq_api_key: str = Field(..., env="GROQ_API_KEY")  # Changed from gemini_api_key to groq_api_key
    linkedin_access_token: str = Field(..., env="LINKEDIN_ACCESS_TOKEN")
    linkedin_person_id: str = Field(..., env="LINKEDIN_PERSON_ID")
    
    # Application Settings
    app_name: str = Field("LinkedIn Post Automation", env="APP_NAME")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Security
    secret_key: str = Field("your-secret-key-here", env="SECRET_KEY")
    
    # Database
    database_url: str = Field("sqlite:///./app.db", env="DATABASE_URL")
    
    # Rate Limiting
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(3600, env="RATE_LIMIT_WINDOW")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    """Get application settings"""
    return Settings()