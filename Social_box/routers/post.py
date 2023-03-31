from fastapi import APIRouter, status, Depends, File, UploadFile, Request, Form
from Social_box import schemas, database, models, oauth2
from sqlalchemy.orm import Session
from typing import List
from Social_box.repository import post
import os

router = APIRouter(tags=["Post"])

file_path = os.path.realpath(os.curdir)

# route to create the post
@router.post("/create_post", status_code=status.HTTP_201_CREATED)
def create_post(
    caption: str = Form(...),
    likes: int = Form(...),
    created_on: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: schemas.user = Depends(oauth2.get_current_user),
):
    return post.create(db, caption, likes, created_on, file, current_user)


# route to get all post irrespective of user
@router.get("/getAllPost")
def getAllPost(
    page_start: int = 1,
    page_end: int = 4,
    db: Session = Depends(database.get_db),
    current_user: schemas.user = Depends(oauth2.get_current_user),
):
    return post.get(page_start, page_end, db, current_user)


# route to get post by id
@router.get("/getPostById/{id}", response_model=schemas.showPost)
def getPostById(
    id: str,
    db: Session = Depends(database.get_db),
    current_user: schemas.user = Depends(oauth2.get_current_user),
):
    return post.getById(id, db, current_user)


# route to delete the post using its id
@router.delete("/delete_post/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletePost(
    id: str,
    db: Session = Depends(database.get_db),
    current_user: schemas.user = Depends(oauth2.get_current_user),
): 
    return post.delete(id, db)


# route to like the post using its id
@router.put("/likePost/{id}", status_code=status.HTTP_202_ACCEPTED)
def likePost(
    id: str,
    db: Session = Depends(database.get_db),
    current_user: schemas.user = Depends(oauth2.get_current_user),
):
    return post.likePost(id, db, current_user)


# route to update the caption of the post using id
@router.put("/update_caption/{id}/{caption}", status_code=status.HTTP_202_ACCEPTED)
def updatePost(
    id: str,
    caption: str,
    db: Session = Depends(database.get_db),
    current_user: schemas.user = Depends(oauth2.get_current_user),
):
    return post.update(id, caption, db)
