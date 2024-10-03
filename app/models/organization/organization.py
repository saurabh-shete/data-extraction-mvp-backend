# app/models/organization.py
import uuid
from sqlalchemy import Column, String, UUID, Text, Enum
from app.initializers.db import Base
from enum import Enum as PyEnum

# Enum for role types
class RoleType(PyEnum):
    admin = "admin"
    internal = "internal"
    user = "user"

class Organization(Base):
    __tablename__ = 'tb_organization'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(Text, nullable=True)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    role_type = Column(Enum(RoleType), nullable=False)
    password = Column(Text, nullable=False)
    mobile_number = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Organization(id={self.id}, username={self.username}, email={self.email})>"