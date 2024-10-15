from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: str  # UUID should be a string, not an integer
    username: str
    email: str

    # New Pydantic v2.0 Config
    class Config:
        from_attributes = True  # Replaces orm_mode

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str