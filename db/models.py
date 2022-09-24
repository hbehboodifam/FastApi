from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base


# User Class (database)
class DbUser(Base):
    __tablename__ = "users"

    user_id = Column(Integer,
                     primary_key=True,
                     index=True)
    user_name = Column(String)
    email = Column(String)
    password = Column(String)

    post = relationship("DbPost", back_populates="user")


# Posts Class (database)
class DbPost(Base):
    __tablename__ = "posts"

    post_id = Column(Integer,
                     primary_key=True,
                     index=True)
    image_url = Column(String)
    image_url_type = Column(String)
    caption = Column(String)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.user_id"))

    user = relationship("DbUser", back_populates="post")
