from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.modules.user import schemas, service
from src.dependencies import get_db
from src.utils.helpers.response_helper import OK, throw_error

router = APIRouter( prefix="/users", tags=["Users"])

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    try:
        user = service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user_out = schemas.UserOut.model_validate(user)
        user_out = user_out.model_dump()
        return OK(status_code=status.HTTP_200_OK, data=user_out)
    except HTTPException as e:
        return throw_error(status_code=e.status_code, error_message=e.detail)
    except Exception as e:
        print(e)
        return throw_error(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, error_message="Internal Server Error")