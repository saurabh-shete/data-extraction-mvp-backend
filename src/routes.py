# src/routes.py
from src.modules.extraction.router import router as extraction_router
from src.modules.organization.router import router as organization_router
from src.modules.auth.router import router as auth_router
from src.modules.user.router import router as user_router

# List of all routes
routes = [
    organization_router,
    auth_router,
    user_router,
    extraction_router,  # Add this line
]