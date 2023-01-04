from sqlalchemy.orm import Session
from Social_box import models, schemas, oauth2
from fastapi import HTTPException, status, Depends
from Social_box.hashing import hashing

# view user's all detail with id
def getUserWithId(id, db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    users = db.query(models.User).filter(models.User.id == id).first()
    profile = db.query(models.Profile).filter(models.Profile.user_id == id).first()
    curr_user = db.query(models.User).filter(models.User.email == current_user).first()
    follow = db.query(models.Followers).filter(models.Followers.user == id, models.Followers.follower == curr_user.id).first()
    curr_user_picture = db.query(models.Profile).filter(models.Profile.user_id == id).first()
    if not follow:
        followed = False
    else:
        followed = True
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id {id} is not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'detail': f'User with id {id} is not found'}
    for i in users.all_post:
        user = db.query(models.User).filter(models.User.id == i.user_id).first()
        user_Picture = db.query(models.Profile).filter(models.Profile.user_id == i.user_id).first()
        likedByCurrUser = db.query(models.PostLikes).filter(models.PostLikes.post_id == i.id,
                                                            models.PostLikes.email == current_user).first()
        if not likedByCurrUser:
            liked = False
        else:
            liked = True
        i.first_name = user.first_name
        i.last_name = user.last_name
        i.profile_pic = user_Picture.profile_pic
        i.liked = liked
    users.profile_pic = curr_user_picture.profile_pic
    users.followed = followed
    users.noOfPost = db.query(models.Post).filter(models.Post.user_id == id).count()
    users.bio = profile.bio
    users.followers = profile.followers
    users.following = profile.following
    return users

# get detail for current user with all post for current user
def getCurrentUser(db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    current_userId = db.query(models.User).filter(models.User.email == current_user).first()
    users = db.query(models.User).filter(models.User.id == current_userId.id).first()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'detail': f'User with id {id} is not found'}
    for i in users.all_post:
        user = db.query(models.User).filter(models.User.id == i.user_id).first()
        user_Picture = db.query(models.Profile).filter(models.Profile.user_id == i.user_id).first()
        likedByCurrUser = db.query(models.PostLikes).filter(models.PostLikes.post_id == i.id, models.PostLikes.email == current_user).first()
        if not likedByCurrUser:
            liked = False
        else:
            liked = True
        i.first_name = user.first_name
        i.last_name = user.last_name
        i.profile_pic = user_Picture.profile_pic
        i.liked = liked
    return users

# route for creating user
def create(request: schemas.user, db: Session):
    new_user = models.User(first_name=request.first_name, last_name=request.last_name, email=request.email, password=hashing.bcrypt(request.password))  # **request.dict() for insert all field at a time
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# route for updating the user detail
def update(id: int, request: schemas.user, db: Session):
    users = db.query(models.User).filter(models.User.id == id)
    if not users.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id {id} is not found')
    users.update(request.dict())
    db.commit()
    return "Updated Successfully"

# route to delete the user with id
def delete(id:int, db: Session):
    user = db.query(models.User).filter(models.User.id == id).delete()
    db.commit()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user with id {id} Not found')
    return "User Deleted Successfully"
