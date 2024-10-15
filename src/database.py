from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from src.config import settings
import logging

Base = declarative_base()

# Initialize variables
SessionLocal = None
engine = None

print(f"Using {settings.environment} environment")
# Conditional logic based on the environment
if settings.environment == "production":
    SUPABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"
    engine = create_engine(SUPABASE_URL, echo=False)
else:
    # Ensure we're using the correct local DATABASE_URL in development
    DATABASE_URL = settings.database_url
    engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get the database session
def get_db():
    try:
        logging.info(f"Using {'Supabase' if settings.environment == 'production' else 'local PostgreSQL'} for database connection")
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        logging.error(f"Error in get_db: {e}")
        raise