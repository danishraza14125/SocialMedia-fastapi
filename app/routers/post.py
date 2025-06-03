from fastapi import FastAPI, HTTPException, Response, status, Depends , APIRouter
from sqlalchemy.orm import session,joinedload
from app.db import models 
from app import schemas,utils, oauth2
from app.schemas import DeletePostsRequest
from app.db.database import engine, get_db
from typing import List
from sqlalchemy import func

router = APIRouter(
      prefix='/posts',
      tags=['Posts']
)

@router.get("/sqlalchemy")
async def test_posts(db : session = Depends(get_db)):
     posts = db.query(models.Post).all() 
#      print(posts)
#      print("printing my sql query")
     return {"Data"   "Succesful" : posts }

# This API to get all data 
@router.get('/', response_model=List[schemas.PostOut])
async def Get_Post(db : session = Depends(get_db), user_id : int = Depends(oauth2.GetCurrentUser)):
#     cursor.execute(""" SELECT * FROM posts""")
#     posts = cursor.fetchall()
      # posts = db.query(models.Post).all()
      posts = db.query(models.Post).options(joinedload(models.Post.owner)).all()

      results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).all()


      return  results

# This API with endpoint "/posts" is for creating new post
@router.post('/', status_code=status.HTTP_201_CREATED, response_model= schemas.Post)
async def Create_Post(post : schemas.PostCreate, db: session = Depends(get_db), current_user : int = Depends(oauth2.GetCurrentUser) ):
      #     cursor.execute(""" INSERT INTO posts(title,content,published) 
      #                    VALUES (%s,%s,%s) RETURNING *""",
      #                    (post.title, post.content, post.published))
      #     new_post = cursor.fetchone()
      #      conn.commit()
      # print(**post.dict())  
      # print(current_user.email)
      new_post = models.Post(owner_id=current_user.id,**post.dict())
      db.add(new_post)
      db.commit()
      db.refresh(new_post)
      return new_post




# API to get the latest post added
# @app.get("/posts/latest")
# async def get_latest_post():
#     try:
#         cursor.execute("""SELECT * FROM posts ORDER BY id DESC LIMIT 1""")
#         latest_post = cursor.fetchone()
#         if not latest_post:
#             raise HTTPException(status_code=404, detail="No posts found")
#         return {"detail": latest_post}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error fetching latest post: {str(e)}")



#  API: Get a single post by ID
@router.get("/{id}", response_model=schemas.PostOut)
async def get_one_post(id: int,  db: session = Depends(get_db), user_id : int = Depends(oauth2.GetCurrentUser)  ):
    
      #   cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
      #   post = cursor.fetchone()
        # post = db.query(models.Post).filter(models.Post.id == id).first()
        
        post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

      #   print(post)
        if not post:
                  raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND,
                  detail=f"Post with id {id} not found"                 
            )
    
        return post
   


# API: Delete a specific post by id 
@router.delete("/{id}")
def delete_post(id: int, db: session = Depends(get_db), current_user : int = Depends(oauth2.GetCurrentUser) ):
    # Retrieve the post
    post = db.query(models.Post).filter(models.Post.id == id).first()

    # Check if the post exists
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"The post with id {id} does not exist")
    
    if post.owner_id != current_user.id :
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                              detail=f"Not authorized to perform requested action")


    # Delete the post
    db.delete(post)
    db.commit()

    return {"message": f"Post with id {id} successfully deleted"}

# API : to delete multipe data records in db by different ids 
# @router.post("/delete")
# def delete_posts(request: DeletePostsRequest, db: session = Depends(get_db), current_user : int = Depends(oauth2.GetCurrentUser) ):
#     posts = db.query(models.Post).filter(models.Post.id.in_(request.ids)).all()
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found for the provided IDs")
    
    
#     for post in posts:
#         db.delete(post)
#     db.commit()
#     return {"message": f"Deleted {len(posts)} posts"}




@router.post("/delete")
def delete_posts(request: DeletePostsRequest, db: session = Depends(get_db), current_user: int = Depends(oauth2.GetCurrentUser)):
    posts = db.query(models.Post).filter(models.Post.id.in_(request.ids)).all()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found for the provided IDs")
    
    unauthorized_posts = [post.id for post in posts if post.owner_id != current_user.id]
    if unauthorized_posts:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Not authorized to delete posts with IDs: {unauthorized_posts}")
    
    for post in posts:
        db.delete(post)
    db.commit()
    return {"message": f"Deleted {len(posts)} posts"}


# API : Update a specific post 
@router.put("/{id}")
def update_post(id: int, updated_post : schemas.PostCreate, db: session = Depends(get_db), current_user : int = Depends(oauth2.GetCurrentUser) ):
      # cursor.execute("""
      #   UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, 
      #   (post.title, post.content, post.published, str(id))) 
      # updated_post = cursor.fetchone()
      # conn.commit()
      post_query = db.query(models.Post).filter(models.Post.id == id)
      post = post_query.first()

      if post == None :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The post with id {id} does not exists")
      
      if post.owner_id != current_user.id :
          raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                              detail=f"Not authorized to perform requested action")

      post_query.update(updated_post.dict(), synchronize_session = False)
      db.commit()

      return{"data :" : post_query.first()}