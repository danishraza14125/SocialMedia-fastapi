from fastapi import APIRouter, Depends , status , HTTPException , Response
from fastapi import APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import  get_db
from app import schemas
from app.db import models
from app import utils
from app import oauth2
from ..oauth2 import CreateAccessToken


router = APIRouter()

@router.post('/login')
def login(user_credentials : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user :
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN, detail= f"Invalid Credentials")
    
    if not utils.passwordVerification(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail= f"Invalid Credentials" )
    
    # print(utils.verify("1234", utils.hash("1234")))  # Should print True

    # access_token = CreateAccessToken(data={"user_id": user.id})
    access_token = CreateAccessToken(data={"sub": str(user.id)})


    return {"access_token" : access_token, "token_type" : "bearer"}

