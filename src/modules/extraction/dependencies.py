# src/modules/extraction/dependencies.py

from fastapi import Depends, HTTPException
from src.database import get_db  # Assuming you have this in src/dependencies.py
from sqlalchemy.orm import Session
from src.config import settings

def get_current_user():
    # Implement authentication dependency if required
    pass

def get_free_ocr_api_key():
    return settings.free_ocr_api_key

def get_openai_client():
    class OpenAIClient:
        api_key = settings.openai_api_key
    return OpenAIClient()