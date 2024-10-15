from pydantic import BaseModel, ConfigDict

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    
    class Config:
        from_attributes = True 

class UserLogin(BaseModel):
    username: str
    password: str