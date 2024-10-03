# app/models/__init__.py

from app.initializers.db import Base, engine
from app.models.organization.organization import Organization

# Create all tables
Base.metadata.create_all(bind=engine)