from datetime import datetime, timedelta
from typing import Optional
import re
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db import models
from db.models import DbUser
from db.schema import UsersFromClient, DisplayUsersToClient
from fastapi import APIRouter, Depends, HTTPException, status
from db.database import get_db
from jose import jwt, JWTError

# Secret key for hashing
SECRET_KEY = "0aee1ca190224da878aeb28213c23a33"
ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Email syntax validation
regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

# Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Check EMAIL syntax
def isValidEmail(email):
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def hash_password(password):
    hashed_password = bcrypt_context.hash(password)
    return hashed_password


def verify_password(plain_password: str, hashed_password: str):
    user = bcrypt_context.verify(plain_password, hashed_password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found!")
    return user


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {
        "sub": username,
        "id": user_id
    }
    if expires_delta is None:
        exp = datetime.utcnow() + timedelta(minutes=15)
    else:
        exp = datetime.utcnow() + expires_delta
    encode.update({"exp": exp})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


# Check if user exist and password matched
def authenticate_user(username, password, db: Session = Depends(get_db)):
    user = db.query(models.DbUser).filter(models.DbUser.user_name == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found!")
    if verify_password(password, user.password) is False:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Password does not match!")
    return user


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/getuser",
            responses={
                200: {
                    "description": "Successful Response",
                    "content": {
                        "application/json": {
                            "example": {
                                "username": "hossein",
                                "id": 1
                            }
                        }
                    }
                },
                401: {
                    "description": "JWT Error",
                    "content": {
                        "application/json": {
                            "example": {
                                "massage": "UNAUTHORIZED"
                            }
                        }
                    }
                },
                404: {
                    "description": "Unknown User",
                    "content": {
                        "application/json": {
                            "example": {
                                "massage": "User not found!"
                            }
                        }
                    }
                }
            })
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    This api gets current user details.

    - **Authentication** is based on oauth2 method.
    - Log in to access the TOKEN
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found!")
        return {
            "username": username,
            "id": user_id
        }
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="UNAUTHORIZED")


@router.post("/", response_model=DisplayUsersToClient,
             summary="Create User",
             responses={
                 422: {
                     "description": "Validation Error",
                     "content": {
                         "application/json": {
                             "example": {
                                 "massage": "The `email` Parameter is not a valid email"
                             }
                         }
                     }
                 }
             })
def create_users(db: Session = Depends(get_db), user_data_from_client: UsersFromClient = None):
    """
    This api creates a user.

    - **Everyone** is able to create user and log in to add some posts
    """
    # create user of class DbUser
    user_data_to_db = DbUser()
    user_data_to_db.user_name = user_data_from_client.user_name
    if isValidEmail(user_data_from_client.email):
        user_data_to_db.email = user_data_from_client.email
    else:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="The `email` Parameter is not a valid email")
    hashed_password = hash_password(user_data_from_client.password)
    user_data_to_db.password = hashed_password
    db.add(user_data_to_db)
    db.commit()
    db.refresh(user_data_to_db)

    return user_data_to_db
