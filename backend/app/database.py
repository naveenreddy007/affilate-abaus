from sqlmodel import SQLModel, create_engine, Session
from .config import settings
import redis

# Database engine
engine = create_engine(settings.database_url, echo=settings.debug)

# Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)


def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session


def get_redis():
    """Get Redis client"""
    return redis_client