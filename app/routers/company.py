from fastapi import APIRouter,status,Depends,HTTPException
from app import schemas,models
from sqlalchemy.orm import Session
from app.database import get_db
from werkzeug.security import generate_password_hash, check_password_hash



router = APIRouter()

@router.post('/register',status_code=status.HTTP_201_CREATED)
def register_company(company:schemas.CompanyCreate,db:Session = Depends(get_db)):
    try:
        existing_company = db.query(models.Company).filter(models.Company.email == company.email).first()

        if existing_company:
            raise HTTPException(status_code=400,detail='Company already registered')
        
        
        new_company = models.Company(
            company_name = company.name,
            phone_number = company.phone_number,
            email = company.email,
            
        )

        db.add(new_company)
        db.commit()
        db.refresh(new_company)
        return {"Message":"Company created succesfully","company_id":new_company.id}
    
    except Exception as error:
        raise HTTPException(status_code=500,detail=error)
        
    
    

