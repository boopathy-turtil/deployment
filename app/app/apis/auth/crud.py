from ...models import *
from ...schemas import *
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database import get_db

def create_cms_user(db, user: UserCreate, cognito_id: str):
    # db: Session = Depends(get_db)
    db_user = CmsUsers(
        id=cognito_id, 
        email=user.email,
        fullName=user.fullName,
        phone=user.phone,
        collegeName=user.collegeName,
        role=user.role,
        status=user.status,
        parentId=user.parentId,
        modelAccess=user.modelAccess,
        logo=user.logo,
        collegeDetails=user.collegeDetails,
        affilliatedUnversity=user.affilliatedUnversity,
        address=user.address,
        resultFormat=user.resultFormat
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user