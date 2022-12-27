from pydantic import BaseModel
from typing import List, Optional


# user related
class user(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

# Post Related
class showPost(BaseModel):
    id: str
    user_id: int
    first_name: str
    last_name: str
    profile_pic: str
    liked: bool
    caption: str
    likes: int
    created_on: str
    web_url: str
    thumbnail_url: Optional[str]
    isImage: bool

    class Config:
        orm_mode = True

class showPostimg(BaseModel):
    caption: str
    likes: int
    created_on: str

    class Config:
        orm_mode = True


class showUsers(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str

    all_post: List[showPost] = []

    class Config:
        orm_mode = True

class showParticularUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    bio: str
    noOfPost: int
    followers: int
    following: int
    followed: bool
    profile_pic: str

    all_post: List[showPost] = []

    class Config:
        orm_mode = True

# Profile Related
class Profile(BaseModel):
    user_id: int
    bio: str
    followers: int
    following: int
    profile_pic: str
    gender: str
    dob: str
    location: str
    created_on: str

    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    bio: str
    # profile_pic: str
    gender: str
    location: str
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

#  TOKEN RELATED
class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Likes of Post
class Likes(BaseModel):
    postId: str
    email: str


class Follower(BaseModel):
    user: int
    follower: int
