
from fastapi import FastAPI
from app.db import models 
from app.db.database import engine
from app.routers.post import router as post_router
from app.routers.user import router as user_router
from app.routers.auth import router as auth_router
from app.routers.vote import router as vote_router
from .config import settings
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind = engine)

origins=["*"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(post_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(vote_router)

@app.get('/')
def root():
    return{"message" : "hello world"}
# app.include_router(user.router) 