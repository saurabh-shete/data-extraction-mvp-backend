from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config.config import settings  
import app.models
import logging

environment = settings.environment


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This is the startup event
    yield
    # This is the shutdown event
    logging.info("Application shutdown logic here.")

# Initialize FastAPI app
if environment == "development":
    app = FastAPI(debug=True,lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
)
