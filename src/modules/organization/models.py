# src/organization/models.py
from sqlalchemy import Column, Integer, String
from src.database import Base

class Organization(Base):
    __tablename__ = 'tb_organizations'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

