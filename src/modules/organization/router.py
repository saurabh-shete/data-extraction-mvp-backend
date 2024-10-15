# src/organization/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import schemas, service
from src.database import get_db

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.post("/", response_model=schemas.OrganizationOut)
def create_organization(org: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    return service.create_organization(db, org)

@router.get("/{org_id}", response_model=schemas.OrganizationOut)
def get_organization(org_id: int, db: Session = Depends(get_db)):
    return service.get_organization(db, org_id)

@router.get("/", response_model=list[schemas.OrganizationOut])
def get_organizations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return service.get_organizations(db, skip=skip, limit=limit)

@router.delete("/{org_id}")
def delete_organization(org_id: int, db: Session = Depends(get_db)):
    service.delete_organization(db, org_id)
    return {"message": "Organization deleted"}

@router.put("/{org_id}", response_model=schemas.OrganizationOut)
def update_organization(org_id: int, org: schemas.OrganizationUpdate, db: Session = Depends(get_db)):
    return service.update_organization(db, org_id, org)
