from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db.database import get_db
from user import authenticate_user, create_access_token

# Define tags and prefix
router = APIRouter(
    tags=["Login to get TOKEN"]
)


@router.post('/token',
             responses={
                 200: {
                     "description": "Successful Response",
                     "content": {
                         "application/json": {
                             "example": {
                                 "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJob3NzZWluIiwiaWQiOjEsImV4cCI6MTY2NDA1NTYxMX0.VTGScVPPMLiccO00IyWkifyasbUsxxR2Jg5cAINk7U4",
                                 "token_type": "Bearer"
                             }
                         }
                     }
                 },
                 404: {
                     "description": "Validation Error",
                     "content": {
                         "application/json": {
                             "example": {
                                 "massage": "User Not Found!"
                             }
                         }
                     }
                 }
             })
def get_token(form_data: OAuth2PasswordRequestForm = Depends(),
              db: Session = Depends(get_db)):
    """
    This api create JWT.

    - Log in to access the TOKEN
    """
    user = authenticate_user(form_data.username,
                             form_data.password,
                             db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User Not Found!")
    token = create_access_token(username=form_data.username,
                                user_id=user.user_id)
    return {
        "access_token": token,
        "token_type": 'Bearer'
    }
