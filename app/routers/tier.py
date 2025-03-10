from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from app.schemas import TierCreate
from app.models import Tier
from app.database import get_db

router = APIRouter()

@router.post('/')
def add_a_tier(request:TierCreate,db:Session=Depends(get_db)):
    try: 

        new_tier = Tier(name=request.name,description=request.description,amount=request.amount)
        db.add(new_tier)
        db.commit()
        db.refresh(new_tier)

        return {"Tier message":"Tier added succesfully"}

    except Exception as e:
        raise HTTPException(status_code=500,detail=f'{e}')
    
@router.get('/')
def get_my_tiers(db:Session=Depends(get_db)):

    try:
        tiers = db.query(Tier).all()
        return {"tier_info":tiers}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'{e}')



