from datetime import datetime
from pydantic import BaseModel


# User Class (client)
class UsersFromClient(BaseModel):
    user_name: str
    password: str
    email: str

    # Define example value for request
    class Config:
        schema_extra = {
            "example": {
                "user_name": "hossein",
                "password": "StrongP@ssword",
                "email": "h.behboodifam@gmail.com"
            }
        }


# User Class Response Model (client)
class DisplayUsersToClient(BaseModel):
    user_name: str
    email: str

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_name": "hossein",
                "email": "h.behboodifam@gmail.com"
            }
        }


# Posts Class (client)
class PostsFromClient(BaseModel):
    image_url: str
    image_url_type: str
    caption: str
    user_id: int

    class Config:
        schema_extra = {
            "example": {
                "image_url": "https://www.wikihow.com/images/Version-6.jpg",
                "image_url_type": "absolute",
                "caption": "Your Caption"
            }
        }


# To show relational
class User(BaseModel):
    user_name: str

    class Config:
        orm_mode = True


# Posts class (Display to client)
class DisplayPostsToClient(BaseModel):
    user_id: int
    image_url: str
    image_url_type: str
    caption: str
    timestamp: datetime
    user: User

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_id": 1,
                "image_url": "https://www.wikihow.com/images/Version-6.jpg",
                "image_url_type": "absolute",
                "caption": "Your Caption",
                "timestamp": "2022-09-24T21:36:42.254Z",
                "user": {
                    "user_name": "hossein"
                }
            }
        }
