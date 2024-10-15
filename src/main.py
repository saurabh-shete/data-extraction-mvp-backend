from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings  # Adjusted import for global config
from src.routes import routes  # Import the routes list
from src.models import create_tables  # Import the function to create tables

# Get the environment from the settings
environment = settings.environment

# Initialize FastAPI app
if environment == "development":
    # Create tables only in development mode
    create_tables()
    app = FastAPI(debug=True)
else:
    # Disable docs and redoc in production
    app = FastAPI(docs_url=None, redoc_url=None,debug=True)

# Define allowed origins for CORS (e.g., frontend origin)
origins = [
    "https://de-mvp.onrender.com",  # Your production frontend URL
    "http://localhost:3000",        # Local development URL (optional)
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include all the routes
for route in routes:
    app.include_router(route)

# Example root route
@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the FastAPI application!"}