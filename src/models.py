# src/models.py
from src.database import Base, engine
from src.config import settings
# Import models here
from src.modules.organization.models import Organization 
from src.modules.user.models import User  
# You can import all models and define them under Base
__all__ = ["Base", "Organization", "User"]

# Function to create tables based on the flag
def create_tables():
    if settings.auto_create_tables:  # Refer to the flag from your settings
        from src.modules.organization.models import Organization
        from src.modules.user.models import User
        # Create all tables
        Base.metadata.create_all(bind=engine)