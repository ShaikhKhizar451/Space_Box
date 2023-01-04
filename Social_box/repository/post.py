from Social_box import schemas, models, oauth2
from Social_box.googleDrive import driveDB
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, File, UploadFile, Form, Depends
import os
import json
from threading import Timer

image = ['jpg', 'jpeg', 'png', 'gif']
video = ['mp4', 'WebM', 'OGG', 'mkv']

# function to create post (This post will be saved in cloud and accept only video and image format)
def create(db: Session, caption: str = Form(...), likes: str = Form(...), created_on: str = Form(...), file: UploadFile = File(...), current_user: schemas.user = Depends(oauth2.get_current_user)):
    userid = db.query(models.User).filter(models.User.email == current_user).first()
    f = open(os.path.realpath(os.curdir)+'/Social_box/temp/'+file.filename+'.'+(file.content_type.split('/')[1]), 'wb')
    f.write(file.file.read())
    f.close()
    id = driveDB.upload_file(file.filename, os.path.realpath(os.curdir)+'/Social_box/temp/'+file.filename+'.'+(file.content_type.split('/')[1]), file.content_type)
    weburl = driveDB.get_file_with_id(id).get('webContentLink')
    if file.content_type.split('/')[1] in image:
        boolImage = True
        thumbnail_url = 'https://drive.google.com/thumbnail?id=' + id
    else:
        boolImage = False
        thumbnail_url = ' '
    new_post = models.Post(id=id, caption=caption, likes=likes, isImage=boolImage, created_on=created_on, user_id=userid.id, web_url=weburl, thumbnail_url=thumbnail_url)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    os.remove(os.path.realpath(os.curdir) + '/Social_box/temp/' + file.filename + '.' + (file.content_type.split('/')[1]))
    return "Post Created Successfully"

# function to get all post with pagination to reduce the time to load data at front end and also to reduce cellular data
def get(page_start: int, page_end: int, db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    posts = db.query(models.Post).all()
    for i in posts:
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
        i.user_id = user.id
    posts.reverse()
    data_length = len(posts)
    start = (page_start - 1) * page_end
    end = start + page_end
    response = {
        "data": posts[start:end],
        "total": data_length,
        "count": end,
        "pagination": {}
    }
    if end >= data_length:
        response["pagination"]["next"] = None
        if page_start > 1:
            response["pagination"]["previous"] = f"/getAllPost?page_start={page_start-1}&page_end={page_end}"
        else:
            response["pagination"]["previous"] = None
    else:
        if page_start > 1:
            response["pagination"]["previous"] = f"/getAllPost?page_start={page_start-1}&page_end={page_end}"
        else:
            response["pagination"]["previous"] = None
        response["pagination"]["next"] = f"/getAllPost?page_start={page_start+1}&page_end={page_end}"
    return response

# function to get post by id
def getById(id: str, db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} is not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'detail': f'User with id {id} is not found'}
    user = db.query(models.User).filter(models.User.id == post.user_id).first()
    user_Picture = db.query(models.Profile).filter(models.Profile.user_id == post.user_id).first()
    likedByCurrUser = db.query(models.PostLikes).filter(models.PostLikes.post_id == post.id, models.PostLikes.email == current_user).first()
    if not likedByCurrUser:
        liked = False
    else:
        liked = True
    post.first_name = user.first_name
    post.last_name = user.last_name
    post.profile_pic = user_Picture.profile_pic
    post.liked = liked
    post.user_id = user.id
    return post

# function to delete post by id
def delete(id: str, db: Session):
    driveDB.delete_file(id)
    post = db.query(models.Post).filter(models.Post.id == id).delete()
    db.commit()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} Not found')
    return "Post Deleted Successfully"

# function to update the post caption by id in db
def update(id: str, request: str, db: Session):
    post = db.query(models.Post).filter(models.Post.id == id).update({"caption": request})
    db.commit()
    return "Updated Successfully"

# function to like the post by id (if user already liked the post it will remove entry from db or else it will be added)
def likePost(id: str, db: Session, current_user: schemas.user = Depends(oauth2.get_current_user)):
    like_filter = db.query(models.PostLikes).filter(models.PostLikes.post_id == id, models.PostLikes.email == current_user).first()
    if not like_filter:
        new_like = models.PostLikes(post_id=id, email=current_user)
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
        curr_like = db.query(models.Post).filter(models.Post.id == id).first()
        db.query(models.Post).filter(models.Post.id == id).update({"likes": curr_like.likes+1})
        db.commit()
        return "liked"
    else:
        del_like = db.query(models.PostLikes).filter(models.PostLikes.post_id == id).delete()
        db.commit()
        curr_like = db.query(models.Post).filter(models.Post.id == id).first()
        db.query(models.Post).filter(models.Post.id == id).update({"likes": curr_like.likes-1})
        db.commit()
        return "unliked"
