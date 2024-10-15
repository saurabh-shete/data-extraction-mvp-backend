# src/modules/extraction/router.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from src.modules.extraction import service
from src.modules.extraction.dependencies import get_current_user
from src.dependencies import get_db
from src.utils.helpers.response_helper import OK, throw_error
import logging

router = APIRouter(
    prefix="/extraction",
    tags=["Extraction"]
)

@router.post("/process")
async def process_file_endpoint(
    file: UploadFile = File(...),
    # current_user = Depends(get_current_user),  # Uncomment if authentication is needed
    db: Session = Depends(get_db)
):
    try:
        result = await service.process_file(file)
        return OK(status_code=status.HTTP_200_OK, data=result)
    except HTTPException as e:
        logging.error(f"HTTPException: {e.detail}")
        return throw_error(status_code=e.status_code, error_message=e.detail)
    except Exception as e:
        logging.exception("Unhandled Exception")
        return throw_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal Server Error"
        )