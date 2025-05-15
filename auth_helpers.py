import logging
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from users import USERS, verify_password  

security = HTTPBasic()  

# Authentication logic
def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    print("Running authenticate_user...")  # Debug print
    logging.info(f"Authenticating user: {credentials.username}")
    user_data = USERS.get(credentials.username)
    
    if user_data and verify_password(credentials.password, user_data["password"]):
        return {"username": credentials.username, "role": user_data["role"]}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

