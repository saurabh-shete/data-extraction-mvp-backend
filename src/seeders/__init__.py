# src/seeders/__init__.py
from src.seeders.organization import seed_organizations
# Future seeders (e.g., user, posts) can be added here as well

def run_seeders():
    print("Starting to seed data...")

    seed_organizations()
    # Call other seeding functions here if needed
    # seed_users()
    # seed_posts()

    print("Finished seeding data.")
