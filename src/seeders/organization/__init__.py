# src/seeders/organization/__init__.py
from src.database import SessionLocal
from src.modules.organization.models import Organization
from src.utils.helpers.encryption_helper import encrypt

def seed_organizations():
    db = SessionLocal()

    organizations = [
        Organization(
            name="Organization 1",
            username="org1",
            email="org1@gmail.com",
            password=encrypt("org1"),
            mobile_number="1234567890"
        ),
        Organization(
            name="Organization 2",
            username="org2",
            email="org2@gmail.com",
            password=encrypt("org2"),
            mobile_number="0987654321"
        ),
    ]

    # Add the organizations to the database session and commit
    db.add_all(organizations)
    db.commit()
    db.close()

    print("Seeded organizations successfully.")
