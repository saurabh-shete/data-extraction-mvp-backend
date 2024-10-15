# src/modules/extraction/schemas.py

from pydantic import BaseModel
from typing import Optional

class ExtractionResponse(BaseModel):
    result: str  # The assistant's response

class ExtractionRequest(BaseModel):
    # If you need to accept additional data besides the file, define here
    pass