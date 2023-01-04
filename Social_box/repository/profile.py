from sqlalchemy.orm import Session
from Social_box import models, schemas, oauth2
from Social_box.googleDrive import driveDB
from fastapi import HTTPException, status, Depends, File, UploadFile, Form
import os
import random

# function to get all profiles from db
def get(db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    profile = db.query(models.Profile).all()
    return profile

# function to get current profile only
def getCurrentProfile(db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    current_userId = db.query(models.User).filter(models.User.email == current_user).first()
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_userId.id).first()
    noOfPost = db.query(models.Post).filter(models.Post.user_id == current_userId.id).count()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Profile not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'detail': f'User with id {id} is not found'}
    return [profile, current_userId.first_name, current_userId.last_name, current_userId.email, noOfPost]

# function to create new profile specific to every user(one user will have only one profile)
def create(db: Session, bio: str = Form(...), gender: str = Form(...), dob: str = Form(...), location: str = Form(...), file: UploadFile = File(...), current_user: schemas.user = Depends(oauth2.get_current_user)):
    current_userId = db.query(models.User).filter(models.User.email == current_user).first()
    f = open(os.path.realpath(os.curdir) + '/Social_box/temp/' + file.filename + '.' + (file.content_type.split('/')[1]), 'wb')
    f.write(file.file.read())
    f.close()
    id = driveDB.upload_file(file.filename, os.path.realpath(os.curdir) + '/Social_box/temp/' + file.filename + '.' + (
    file.content_type.split('/')[1]),file.content_type)
    weburl = driveDB.get_file_with_id(id).get('webContentLink')
    new_profile = models.Profile(user_id=current_userId.id, bio=bio, followers=0, following=0, profile_pic=weburl, gender=gender, dob=dob, location=location)  # **request.dict() for insert all field at a time
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    os.remove(os.path.realpath(os.curdir) + '/Social_box/temp/' + file.filename + '.' + (file.content_type.split('/')[1]))
    return "Profile Created Successfully"

# function to update current user details
def update(user_id: int, media_id: int, db: Session, bio: str = Form(...), gender: str = Form(...), location: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), file: UploadFile = File(...)):
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id)
    user = db.query(models.User).filter(models.User.id == user_id)

    f = open(
        os.path.realpath(os.curdir) + '/Social_box/temp/' + file.filename + '.' + (file.content_type.split('/')[1]),
        'wb')
    f.write(file.file.read())
    f.close()

    driveDB.update_file(media_id, os.path.realpath(os.curdir) + '/Social_box/temp/' + file.filename + '.' + (
    file.content_type.split('/')[1]), file.content_type)

    if not profile.first() and user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Profile/User with id {user_id} is not found')
    profile.update({'bio': bio, 'gender': gender, 'location': location})
    db.commit()
    user.update({'first_name': first_name, 'last_name': last_name})
    db.commit()
    os.remove(
        os.path.realpath(os.curdir) + '/Social_box/temp/' + file.filename + '.' + (file.content_type.split('/')[1]))
    return "Updated Successfully"

# function to delete user with id
def delete(id:int, db: Session):
    profile = db.query(models.Profile).filter(models.Profile.profile_id == id).delete()
    db.commit()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Profile with id {id} Not found')
    return "User Deleted Successfully"

# function to follow user (if current user already followed the respective user it will remove the entry from db or else it will add)
def follow(id: str, db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    curr_user = db.query(models.User).filter(models.User.email == current_user).first()
    follow_filter = db.query(models.Followers).filter(models.Followers.user == id, models.Followers.follower == curr_user.id).first()
    if not follow_filter:
        new_follow = models.Followers(user=id, follower=curr_user.id)
        db.add(new_follow)
        db.commit()
        db.refresh(new_follow)
        curr_followers = db.query(models.Profile).filter(models.Profile.user_id == id).first()
        db.query(models.Profile).filter(models.Profile.user_id == id).update({"followers": curr_followers.followers+1})
        db.commit()
        curr_following = db.query(models.Profile).filter(models.Profile.user_id == curr_user.id).first()
        db.query(models.Profile).filter(models.Profile.user_id == curr_user.id).update({"following": curr_following.following+1})
        db.commit()
        return "follow"
    else:
        db.query(models.Followers).filter(models.Followers.user == id).delete()
        db.commit()
        curr_followers = db.query(models.Profile).filter(models.Profile.user_id == id).first()
        db.query(models.Profile).filter(models.Profile.user_id == id).update({"followers": curr_followers.followers-1})
        db.commit()
        curr_following = db.query(models.Profile).filter(models.Profile.user_id == curr_user.id).first()
        db.query(models.Profile).filter(models.Profile.user_id == curr_user.id).update({"following": curr_following.following-1})
        db.commit()
        return "unfollow"

# function to get suggested user (this will return the random users which is not followed by current user)
def suggestionUser(db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    curr_user = db.query(models.User).filter(models.User.email == current_user).first()
    following = db.query(models.Followers).filter(models.Followers.follower == curr_user.id).values(models.Followers.user)
    all_user = db.query(models.Profile.user_id).all()
    foll = []
    user = []
    for i in following:
        foll.append(i[0])
    for i in all_user:
        user.append(i[0])
    [user.remove(item) for item in foll if item in user]
    suggestUser = []
    for i in user:
        newSuggestUser = db.query(models.Profile).filter(models.Profile.user_id == i).first()
        newSuggestUser.first_name = db.query(models.User).filter(models.User.id == newSuggestUser.user_id).value(models.User.first_name)
        newSuggestUser.last_name = db.query(models.User).filter(models.User.id == newSuggestUser.user_id).value(models.User.last_name)
        if curr_user.id != newSuggestUser.user_id:
            finalUser = {'user_id': newSuggestUser.user_id, 'profile_pic': newSuggestUser.profile_pic, 'location': newSuggestUser.location, 'first_name': newSuggestUser.first_name, 'last_name': newSuggestUser.last_name}
            suggestUser.append(finalUser)
    random.shuffle(suggestUser)
    return suggestUser[:4]
