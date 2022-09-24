import datetime
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db import models
from db.database import get_db
from db.models import DbPost
from db.schema import PostsFromClient, DisplayPostsToClient
from jose import JWTError
from user import get_current_user

# Define tags and prefix
router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

oauth2_schema = OAuth2PasswordBearer(tokenUrl='token')

# Restrict request in desire format
image_url_types = ['relative', 'absolute']


@router.post("/", response_model=DisplayPostsToClient,
             responses={
                 422: {
                     "description": "Unprocessable Entity",
                     "content": {
                         "application/json": {
                             "example": {
                                 "massage": "The `image_url_type` Parameter should be -absolute- or -relative-"
                             }
                         }
                     }
                 }
             }
             )
def create_post(db: Session = Depends(get_db),
                posts_data_from_user: PostsFromClient = None,
                current_user=Depends(get_current_user)):
    posts_to_database = DbPost()
    posts_to_database.caption = posts_data_from_user.caption
    posts_to_database.image_url = posts_data_from_user.image_url
    if not posts_data_from_user.image_url_type in image_url_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The `image_url_type` Parameter should be -absolute- or -relative-"
        )
    posts_to_database.image_url_type = posts_data_from_user.image_url_type
    posts_to_database.timestamp = datetime.datetime.now()
    posts_to_database.user_id = posts_data_from_user.user_id

    db.add(posts_to_database)
    db.commit()
    db.refresh(posts_to_database)

    return posts_to_database


@router.delete("/",
               responses={
                   200: {
                       "description": "Successful Response",
                       "content": {
                           "application/json": {
                               "example": {
                                   "status:": "done"
                               }
                           }
                       }
                   },
                   401: {
                       "description": "Permission Error",
                       "content": {
                           "application/json": {
                               "example": {
                                   "massage": "The post is not created by this user!"
                               }
                           }
                       }
                   },
                   404: {
                       "description": "Unknown Post",
                       "content": {
                           "application/json": {
                               "example": {
                                   "massage": "No post found!"
                               }
                           }
                       }
                   }
               }
               )
def delete_post(post_id: int,
                db: Session = Depends(get_db),
                current_user=Depends(get_current_user)):
    post_to_delete = db.query(DbPost).filter(DbPost.post_id == post_id).first()
    if post_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No post found!")
    if current_user.get("id") != post_to_delete.user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="The post is not created by this user!")
    db.query(DbPost).filter(DbPost.post_id == post_id).delete()
    db.commit()
    return {
        "status:": "done"
    }


@router.get("/all",
            summary="Get All Posts",
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": {
                                "massage":
                                    [
                                        {
                                            "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGBEpwrcx9BLcNgCluJrUoR5IGp0UzC7wt7_jQqpU1&s",
                                            "image_url_type": "absolute",
                                            "timestamp": "2022-09-24T23:40:17.268714",
                                            "post_id": 1,
                                            "caption": "Beautiful picture",
                                            "user_id": 1
                                        }
                                    ]
                            }
                        }
                    }
                }
            })
def get_all_posts(db: Session = Depends(get_db)):
    """
    This api gets all posts that is created by any user.

    - It isn't necessary to be logged in to retrieve posts.
    """
    return db.query(DbPost).all()
