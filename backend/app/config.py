from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/affiliate_db"
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Razorpay
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Application
    debug: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()