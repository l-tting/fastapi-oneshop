from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user
# from utils import admin_required


router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
# @admin_required
def register_vendor(vendor: schemas.VendorCreate, user=Depends(get_current_user), db: Session = Depends(get_db)):
    existing_vendor = db.query(models.Vendor).filter(models.Vendor.email == vendor.email).first()
    if existing_vendor:
        raise HTTPException(status_code=400, detail="Vendor already exists")
    new_vendor = models.Vendor(
        name=vendor.name, 
        phone_number=vendor.phone_number, 
        email=vendor.email,
        address=vendor.address
    )
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    return {"message": "Vendor added successfully"}
