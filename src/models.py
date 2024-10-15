# src/models.py
from src.database import Base, settings

# Import engine only in development mode
if settings.environment != "production":
    from src.database import engine

# Import models here
from src.modules.organization.models import Organization 
from src.modules.user.models import User  
__all__ = ["Base", "User"]

# Function to create tables based on the environment
def create_tables():
    if settings.auto_create_tables and settings.environment == "development":
        # Create tables only in development mode (local PostgreSQL)
        Base.metadata.create_all(bind=engine)