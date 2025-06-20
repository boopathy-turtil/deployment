from fastapi import APIRouter, UploadFile, File, HTTPException,Form,Depends
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from typing import List
from ... import  schemas, models
from ...models import AssignmentDetails,CmsUsers
from ...database import get_db
import zipfile
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from uuid import uuid4
from ...schemas import ExamUpdateRequest
from ...tokendecode import get_current_user
from typing import List, Dict, Optional, Any
from datetime import datetime,date



app = APIRouter(prefix="/cms-assignment", tags=["cms-assignment"])
def get_org_id_from_user_id(db: Session, user_id: str) -> str:
    user = db.query(CmsUsers).filter(CmsUsers.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    return user.parentId if user.parentId else user.id

from typing import List, Dict, Optional, Any
from datetime import datetime,date
@app.post("/create-assignment/")
async def create_assignment(
    title: str,
    degree: str,
    branch: str,
    batch: int,
    section: str,
    submission: str,
    dueDate: date,
    marks: int,
    description: Optional[str] = None,
    # file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        print("************",current_user)
        org_id = get_org_id_from_user_id(db, current_user['user_id'])
        print("*************",org_id)
        assignment = db.query(AssignmentDetails).filter_by(title=title, org_id=org_id).first()

        if assignment:
            raise HTTPException(status_code=400, detail="Assignment with this title already exists")

        new_assignment = AssignmentDetails(
            id=str(uuid4()),
            title=title,
            description=description,
            submission=submission,
            dueDate=dueDate,
            marks=marks,
            branch=branch,
            batch=batch,
            section=section,
            org_id=org_id,degree=degree
        )
        db.add(new_assignment)
        db.commit()
        db.refresh(new_assignment)

        return {"message": "Assignment created successfully", "assignment_id": new_assignment.id}

    except Exception as e:
        # You can log the error here if needed
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@app.get("/get-assigment/")
def get_assigment( db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    org_id = get_org_id_from_user_id(db, current_user['user_id'])
    assigment=db.query(AssignmentDetails).filter(AssignmentDetails.org_id==org_id).all()
    return assigment