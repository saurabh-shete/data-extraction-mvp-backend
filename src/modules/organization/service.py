# src/organization/service.py
from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException

def create_organization(db: Session, org: schemas.OrganizationCreate):
    db_org = models.Organization(name=org.name, description=org.description)
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_organization(db: Session, org_id: int):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

def get_organizations(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Organization).offset(skip).limit(limit).all()

def delete_organization(db: Session, org_id: int):
    org = get_organization(db, org_id)
    db.delete(org)
    db.commit()

def update_organization(db: Session, org_id: int, org_data: schemas.OrganizationUpdate):
    org = get_organization(db, org_id)
    org.name = org_data.name
    org.description = org_data.description
    db.commit()
    db.refresh(org)
    return org
