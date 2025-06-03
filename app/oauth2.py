from jose import JWTError , jwt 
from datetime import datetime, timedelta
from . import schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.db import database , models
from sqlalchemy.orm import Session
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# SECRET_KEY
#  Algorithm 
# Expriation time 

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# def CreateAccessToken(data : dict):
#     to_encode = data.copy()

#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})

#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


def CreateAccessToken(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# def VerifyAccessToken(token : str , credential_expection):

    try:
        payload = jwt.decode(token , SECRET_KEY , algorithms= [ALGORITHM])
        # id : str = payload.get("user_id")
        id : str = payload.get("sub")
        

        if id is None:
           raise credential_expection
        
        token_data = schemas.TokenData(id = id )
    except JWTError: 
        raise credential_expection    
    
    return token_data

def VerifyAccessToken(token: str, credential_exception):
    try:
        # print("in verify token function")
        # print(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # print("palyload",payload)
        id: str = payload.get("sub")
        # print("id",id)
        if id is None:
            raise credential_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credential_exception
    return token_data

def GetCurrentUser(token : str = Depends(oauth2_scheme), db : Session = Depends (database.get_db) ):
    # print(f"Received token: {token}")

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail=f"Could not valid credentials",
                                          headers= {"WWW-Authenticate" : "Bearer"})
    
    token = VerifyAccessToken(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id ).first()
    
    return user