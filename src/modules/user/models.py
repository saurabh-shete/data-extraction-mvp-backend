import uuid
from sqlalchemy import Column, String, event
from sqlalchemy.dialects.postgresql import UUID  # Use this for PostgreSQL
from src.database import Base

class User(Base):
    __tablename__ = "tb_user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)  # Using UUID for id
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

@event.listens_for(User, "load")
def receive_load(user, context):
    if isinstance(user.id, uuid.UUID):
        user.id = str(user.id)