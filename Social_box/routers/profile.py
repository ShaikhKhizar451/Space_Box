from fastapi import APIRouter, Depends, Response, status, Form, File, UploadFile
from typing import List
from Social_box import schemas, database, oauth2
from sqlalchemy.orm import Session

from Social_box .repository import profile

router = APIRouter(
    tags=['Profile']
)

# Route to return all profiles
@router.get('/getprofile', response_model=List[schemas.Profile])
def getProfile(db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return profile.get(db, current_user)

# Route to return current profile only
@router.get('/getCurrentProfile')
def getCurrentProfile(db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return profile.getCurrentProfile(db, current_user)

# Route for creating a profile for current user
@router.post('/create_profile', status_code=status.HTTP_201_CREATED)
def create_Profile(bio: str = Form(...), gender: str = Form(...), dob: str = Form(...), location: str = Form(...), file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return profile.create(db, bio, gender, dob, location, file, current_user)

# Route for updating a profile
@router.put('/updateProfile/{user_id}/{media_id}', status_code=status.HTTP_202_ACCEPTED)
def updateProfileDetails(user_id, media_id, bio: str = Form(...), gender: str = Form(...), location: str = Form(...), first_name: str = Form(...), last_name: str = Form(...), file: UploadFile = File(...), db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return profile.update(user_id, media_id, db, bio, gender, location, first_name, last_name, file)

# Route for delete a profile
@router.delete('/deleteProfile/{id}', status_code=status.HTTP_204_NO_CONTENT)
def deleteProfile(id, db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return profile.delete(id, db)

# Route to follow users
@router.put('/follow/{id}', status_code=status.HTTP_202_ACCEPTED)
def follow(id: str, db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return profile.follow(id, db, current_user)

# Route to return suggested users
@router.get('/suggestionUser')
def suggestionUser(db: Session = Depends(database.get_db), current_user: schemas.user = Depends(oauth2.get_current_user)):
    return profile.suggestionUser(db, current_user)
