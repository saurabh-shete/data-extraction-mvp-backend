# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from supabase import create_client, Client
from src.config import settings

Base = declarative_base()

# Initialize variables
SessionLocal = None
supabase = None
engine = None  # Initialize engine as None by default

# Conditional logic based on the environment
if settings.environment == "production":
    # Use Supabase client for production
    supabase_url = settings.supabase_url
    supabase_key = settings.supabase_key
    supabase: Client = create_client(supabase_url, supabase_key)
else:
    # Use local PostgreSQL database for development
    DATABASE_URL = settings.database_url
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get the database session based on the environment
def get_db():
    if settings.environment == "production":
        return supabase
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()