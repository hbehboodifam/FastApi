import uvicorn
from fastapi import FastAPI
import posts
import createtoken
import user
from db import models
from db.database import engine

# Create database (sqlite3)
models.Base.metadata.create_all(bind=engine)

# Create fastapi object
app = FastAPI()

# include routers
app.include_router(user.router)
app.include_router(posts.router)
app.include_router(createtoken.router)


# First page API ("Hello World")
@app.get("/",
         responses={
             200: {
                 "description": "Successful Response",
                 "content": {
                     "application/json": {
                         "example": {
                             "massage": "Hello world!"
                         }
                     }
                 }
             }
         }
         )
def root():
    return "Hello World!"


# Run uvicorn server
uvicorn.run(app)
