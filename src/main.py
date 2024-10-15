# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings  # Adjusted import for global config
from src.routes import routes  # Import the routes list
from src.models import create_tables  # Import the function to create tables

# Get the environment from the settings
environment = settings.environment

# Initialize FastAPI app
if environment == "development":
    create_tables()
    app = FastAPI(debug=True)
else:
    # Disable docs and redoc in production
    app = FastAPI(docs_url=None, redoc_url=None)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this based on your needs
    allow_credentials=True,
    allow_methods=["*"],  # You can restrict specific HTTP methods
    allow_headers=["*"],  # You can restrict specific headers
)

# Include all the routes
for route in routes:
    app.include_router(route)

# Example route (optional)
@app.get("/",tags=["Root"])
def root():
    return {"message": "Welcome to the FastAPI application!"}
