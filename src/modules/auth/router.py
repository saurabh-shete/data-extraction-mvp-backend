from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.modules.auth import schemas, service
from src.modules.auth.dependencies import get_current_user
from src.dependencies import get_db
from src.utils.helpers.response_helper import OK, throw_error

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:

        new_user = service.create_user(db, user)
        user_out = new_user.model_dump()
        return OK(status_code=status.HTTP_201_CREATED, data=user_out)
    except HTTPException as e:
        return throw_error(status_code=e.status_code, error_message=e.detail)
    except Exception as e:
        print(e)
        return throw_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message="Internal Server Error")
    
@router.post("/login", response_model=schemas.Token)
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    try:
        token = service.authenticate_user(db, user)
        return OK(status_code=status.HTTP_200_OK, data=token)
    except HTTPException as e:
        return throw_error(status_code=e.status_code, error_message=e.detail)
    except Exception as e:
        print(e)
        return throw_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message="Internal Server Error")