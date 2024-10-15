# src/routes.py
from src.modules.extraction.router import router as extraction_router
from src.modules.auth.router import router as auth_router
from src.modules.user.router import router as user_router

# List of all routes
routes = [
    auth_router,
    user_router,
    extraction_router,  # Add this line
]