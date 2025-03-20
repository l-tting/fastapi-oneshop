from functools import wraps
from fastapi import FastAPI,Depends,status,HTTPException
def admin_required(f):
    @wraps(f)
    def admin_decorated(user, *args, **kwargs):
        # Check if the current user has the 'admin' role
        if not user or getattr(user, 'role', None) != 'admin':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")
        return f(user=user, *args, **kwargs)
    return admin_decorated

import random

def generate_otp():
    otp = random.randint(100000,999999)
    return otp



     

