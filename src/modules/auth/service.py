from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from src.modules.user import models, schemas
from src.utils.helpers.encryption_helper import encrypt, compare
from src.utils.helpers.jwt_helper import create_access_token
from src.constants.constants import ACCESS_TOKEN_EXPIRE_MINUTES

# Authenticate user and return JWT token
def authenticate_user(db: Session, user: schemas.UserLogin):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not compare(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": str(db_user.id)},  # Use the UUID for sub (subject)
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    # Check if the username or email already exists
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    # Encrypt the user's password
    hashed_password = encrypt(user.password)

    # Create a new user record
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    # Add the new user to the database and commit the transaction
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return the user as a Pydantic schema
    user_out = schemas.UserOut(
        id=str(new_user.id),  # Convert UUID to string
        username=new_user.username,
        email=new_user.email
    )

    return user_out