import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

logger = logging.getLogger(__name__)

# Get database URL from environment or use default for local development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://leanin:leanin123@localhost:5432/leanin_impact"
)

# Create engine with connection pooling
# Note: pool_pre_ping=True helps catch stale connections early
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency injection for database sessions.
    
    Ensures proper cleanup and error handling for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
