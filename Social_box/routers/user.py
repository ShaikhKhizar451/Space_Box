from fastapi import APIRouter, Depends, HTTPException, Response, status
from typing import List
from Social_box import schemas, database, models, oauth2
from sqlalchemy.orm import Session

from Social_box .repository import user

router = APIRouter(
    tags=['User']
)

@router.get('/getUserWithId/{id}', response_model=schemas.showParticularUser)
def getUserWithId(id: int, db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return user.getUserWithId(id, db, current_user)

@router.get('/getCurrentUser', response_model=schemas.showUsers)
def getCurrentUser(response: Response, db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return user.getCurrentUser(db, current_user)

@router.post('/create_user', status_code=status.HTTP_201_CREATED, response_model=schemas.showUsers)
def create_user(request: schemas.user, db: Session = Depends(database.get_db)):
    return user.create(request, db)

@router.put('/user/{id}', status_code=status.HTTP_202_ACCEPTED)
def updateUserDetails(id, request: schemas.user, db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return user.update(id, request, db)

@router.delete('/user/{id}', status_code=status.HTTP_204_NO_CONTENT)
def deleteUser(id, db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return user.delete(id, db)
