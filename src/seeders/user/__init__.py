from src.database import SessionLocal
from src.modules.user.models import User
from src.utils.helpers.encryption_helper import encrypt

def seed_users():
    db = SessionLocal()

    users = [
        User(
            username="user1",
            email="user1@example.com",
            hashed_password=encrypt("user1")
        ),
    ]

    # Add the users to the database session and commit
    db.add_all(users)
    db.commit()
    db.close()

    print("Seeded users to local PostgreSQL database successfully.")