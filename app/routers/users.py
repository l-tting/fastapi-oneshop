from fastapi import APIRouter, Depends, HTTPException, status,Query
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from app import models, schemas
from app.database import get_db
from app.auth import create_access_token
from datetime import timedelta
from app.utils import generate_otp
from routers.email import fm

router = APIRouter()

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)

def register_user(user: schemas.User,company_id :int=Query(...), db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = generate_password_hash(user.password)
    new_user = models.User(
        company_id = company_id,
        full_name=user.full_name,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    registered_user = db.query(models.User).filter(models.User.email == user.email).first()
    if registered_user is None or not check_password_hash(registered_user.password, user.password):
        raise HTTPException(status_code=404, detail="Invalid credentials")
    access_token = create_access_token(data={"user": user.email}, expires_delta=timedelta(days=30))
    return {"access_token": access_token,"current_user":registered_user.full_name}


@router.get("/", status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return {"users": users}


@router.post('/reset_password',status_code=201)
def reset_password(request:schemas.PasswordReset,db:Session=Depends(get_db)):
    registered_user = db.query(models.User).filter(models.User.email==request.email).first()
    if registered_user is None:
        raise HTTPException(status_code=404,detail='User not found,please register')
    
    otp = generate_otp()
    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Password don't match")
    hashed_password = generate_password_hash(request.password)
    registered_user.password = hashed_password
    try:
        db.commit()
        db.refresh(registered_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed tto update password'
        )
    return {
        "Message":"Password changed succesfully",
        "user":registered_user.email
            
            }


