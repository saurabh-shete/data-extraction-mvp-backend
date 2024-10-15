from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import settings
import logging

Base = declarative_base()

# Initialize variables
SessionLocal = None
engine = None  # Initialize engine as None by default

# Conditional logic based on the environment
if settings.environment == "production":
    # Use Supabase PostgreSQL database connection for production
    SUPABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    engine = create_engine(SUPABASE_URL, echo=False)
else:
    # Use local PostgreSQL database for development
    DATABASE_URL = settings.database_url
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get the database session based on the environment
def get_db():
    try:
        logging.info(f"Using {'Supabase' if settings.environment == 'production' else 'local PostgreSQL'} for database connection")
        db = SessionLocal()
        try:
            yield db  # Yield the database session
        finally:
            db.close()
    except Exception as e:
        logging.error(f"Error in get_db: {e}")
        raise