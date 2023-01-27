from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from Social_box.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime

timeFormat = datetime.now().strftime("%Y-%m-%d %H:%M")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    password = Column(String)

    all_post = relationship("Post", back_populates="this_user")
    profile = relationship("Profile", back_populates="profile_user")


class Post(Base):
    __tablename__ = "Post"

    id = Column(String, primary_key=True)
    caption = Column(String)
    likes = Column(Integer, default=1)
    created_on = Column(String, default=timeFormat)
    isImage = Column(Boolean)
    web_url = Column(String)
    thumbnail_url = Column(String)

    user_id = Column(Integer, ForeignKey("user.id"))

    this_user = relationship("User", back_populates="all_post")


class Profile(Base):
    __tablename__ = "Profile"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)

    bio = Column(String)
    followers = Column(Integer)
    following = Column(Integer)
    profile_pic = Column(String)
    gender = Column(String)
    dob = Column(String)
    location = Column(String)
    created_on = Column(String, default=timeFormat)

    profile_user = relationship("User", back_populates="profile")


class PostLikes(Base):
    __tablename__ = "PostLikes"

    index_no = Column(Integer, primary_key=True, index=True)
    post_id = Column(String)
    email = Column(String)


class Followers(Base):
    __tablename__ = "Followers"

    index_no = Column(Integer, primary_key=True, index=True)
    user = Column(Integer)
    follower = Column(Integer)
