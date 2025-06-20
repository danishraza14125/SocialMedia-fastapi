from sqlalchemy.orm import session

from app import schemas, utils
from app.db import models
from app.db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
async def create_user(user: schemas.UserCreate, db: session = Depends(get_db)):

    # hashing the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# This API to get all users
@router.get("/")
async def Get_Post(db: session = Depends(get_db)):
    #     cursor.execute(""" SELECT * FROM posts""")
    #     posts = cursor.fetchall()
    user = db.query(models.User).all()
    return {"Users Data": user}


#  API: Get a single user by ID
@router.get("/{id}", response_model=schemas.UserOut)
async def get_one_user(id: int, db: session = Depends(get_db)):

    #   cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    #   post = cursor.fetchone()
    user = db.query(models.User).filter(models.User.id == id).first()
    #   print(post)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found"
        )
    return user
