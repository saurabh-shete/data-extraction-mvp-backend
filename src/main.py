from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings  # Adjusted import for global config
from src.routes import routes  # Import the routes list
from src.models import create_tables  # Import the function to create tables
import httpx
import asyncio
import os
# Get the environment from the settings
environment = settings.environment
print(os.path.dirname(__file__),"main.py")
# Initialize FastAPI app
if environment == "development":
    # Create tables only in development mode
    create_tables()
    app = FastAPI(debug=True)
else:
    # Disable docs and redoc in production
    app = FastAPI(docs_url=None, redoc_url=None)

# Define allowed origins for CORS (e.g., frontend origin)
origins = [
    "https://de-mvp.onrender.com",  # Your production frontend URL
    "http://127.0.0.1:5173",        # Local development URL (optional)
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

# Background task to ping the server itself
async def ping_self():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://data-extraction-mvp-backend.onrender.com/")
                if response.status_code == 200:
                    print("Ping successful.")
                else:
                    print(f"Ping failed with status code: {response.status_code}")
        except Exception as e:
            print(f"Error pinging self: {e}")
        # Wait for 14 minutes 50 seconds before the next ping
        await asyncio.sleep(14 * 60 + 50)

# Function to start background tasks in production
@app.on_event("startup")
async def startup_event():
    if environment == "production":
        # Start the self-ping task only in production
        asyncio.create_task(ping_self())