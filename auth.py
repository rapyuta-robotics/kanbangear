import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from users import USERS, verify_password  
from auth_helpers import authenticate_user  



def check_admin_role(user: dict = Depends(authenticate_user)):
    print("Running check_admin_role...")  # Debug print
    if user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="You do not have access to this resource")
    return user

