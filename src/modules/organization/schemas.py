# src/organization/schemas.py
from pydantic import BaseModel

class OrganizationBase(BaseModel):
    name: str
    description: str | None = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(OrganizationBase):
    pass

class OrganizationOut(OrganizationBase):
    id: int

    class Config:
        from_attributes = True
