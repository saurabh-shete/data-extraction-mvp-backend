# src/seeders/__init__.py
from src.seeders.user import seed_users
# Future seeders (e.g., user, posts) can be added here as well

def run_seeders():
    print("Starting to seed data...")

    seed_users()

    print("Finished seeding data.")
