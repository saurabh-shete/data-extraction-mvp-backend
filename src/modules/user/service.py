from sqlalchemy.orm import Session
from src.modules.user import models

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()