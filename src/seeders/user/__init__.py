from src.database import SessionLocal, supabase, settings
from src.modules.user.models import User
from src.utils.helpers.encryption_helper import encrypt

def seed_users():
    if settings.environment == "production":
        # Use Supabase to insert users
        users = [
            {
                "username": "user1",
                "email": "user1@example.com",
                "hashed_password": encrypt("user1")
            },
        ]
        for user in users:
            supabase.table("tb_user").insert(user).execute()

        print("Seeded users to Supabase successfully.")

    else:
        # Use local PostgreSQL database to insert users
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