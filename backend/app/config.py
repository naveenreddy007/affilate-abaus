from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


class Settings(BaseSettings):
    # Database Configuration - Using SQLite for testing
    database_url: str = Field(default="sqlite:///./affiliate_db.db")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379")

    # JWT Configuration
    secret_key: str = Field(default="your-super-secret-jwt-key-change-this-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # Email Configuration
    email_from: str = Field(default="noreply@example.com")
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")

    # Razorpay Configuration
    razorpay_key_id: str = Field(default="")
    razorpay_key_secret: str = Field(default="")

    # CORS Configuration
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])

    # Application Configuration
    debug: bool = False
    environment: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()