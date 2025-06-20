from fastapi import FastAPI, HTTPException, Depends, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy import delete, update
from sqlalchemy import and_, or_, exists


import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ...models import ListOfStudents,SharedListAccess,CmsUsers

from ...schemas import *
from ...database import get_db
from ...config import settings

from fastapi import Query
from sqlalchemy.orm import Session
from uuid import uuid4


import pandas as pd
from fastapi.responses import FileResponse
import io






from ...tokendecode import get_current_user

# from fastapi.security import OAuth2PasswordRequestForm




# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = APIRouter(prefix="/cms-list-of-students", tags=["cms-list-of-students"])






# POST API - Create new list
@app.post("/lists/", response_model=ListOfStudentsResponse)
def create_list(list_data: ListOfStudentsCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_list = ListOfStudents(
        id=str(uuid4()),
        listName=list_data.listName,
        listCreatedBy=list_data.listCreatedBy,
        studentList=[student.model_dump() for student in list_data.studentList],
        noOfStudents=len(list_data.studentList)
    )
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list

# GET by ID API
@app.get("/lists/{list_id}", response_model=ListOfStudentsResponse)
def get_list(list_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_list = db.query(ListOfStudents).filter(ListOfStudents.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    return db_list

# GET all API

@app.get("/lists/", response_model=List[ListOfStudentsResponse])
def get_all_lists(
    list_createdby: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user['user_id']

    created_lists = (
        db.query(ListOfStudents)
        .filter(ListOfStudents.listCreatedBy == list_createdby)
        .offset(skip)
        .limit(limit)
        .all()
    )
    for lst in created_lists:
        lst.shared = False 

    shared_lists = (
        db.query(ListOfStudents)
        .join(SharedListAccess, ListOfStudents.id == SharedListAccess.listId)
        .filter(SharedListAccess.sharedWith == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    created_ids = {lst.id for lst in created_lists}
    unique_shared_lists = [lst for lst in shared_lists if lst.id not in created_ids]
    for lst in unique_shared_lists:
        lst.shared = True

    final_list = created_lists + unique_shared_lists

    return final_list

# DELETE by ID API
@app.delete("/lists/{list_id}")
def delete_list(list_id: str, db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    db_list = db.query(ListOfStudents).filter(ListOfStudents.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    db.delete(db_list)
    db.commit()
    return {"message": "List deleted successfully"}

# Add students to studentList API (prepend to list)
@app.post("/lists/{list_id}/students")
def add_students(list_id: str, students: List[CollegeStudentBase], db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_list = db.query(ListOfStudents).filter(ListOfStudents.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    current_students = db_list.studentList or []
    new_students = [student.model_dump() for student in students]
    
    # Prepend new students
    updated_students = new_students + current_students
    db_list.studentList = updated_students
    db_list.noOfStudents = len(updated_students)
    # db_list.updatedAt = get_current_timestamp()
    
    db.commit()
    db.refresh(db_list)
    return db_list

# # Remove students from studentList API
# @app.delete("/lists/{list_id}/students")
# def remove_students(list_id: str, student_ids: List[str], db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
#     db_list = db.query(ListOfStudents).filter(ListOfStudents.id == list_id).first()
#     if not db_list:
#         raise HTTPException(status_code=404, detail="List not found")
    
#     current_students = db_list.studentList or []
#     # Filter out students with matching IDs
#     updated_students = [s for s in current_students if s.get("studentId") not in student_ids]
    
#     db_list.studentList = updated_students
#     db_list.noOfStudents = len(updated_students)
#     # db_list.updatedAt = get_current_timestamp()
    
#     db.commit()
#     db.refresh(db_list)
#     return db_list

# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from typing import List
# from datetime import datetime

# # Assuming these are defined elsewhere
# from your_app.dependencies import get_db, get_current_user
# from your_app.models import ListOfStudents
# from your_app.utils import get_current_timestamp

# router = APIRouter()

# # Request body model
# class RemoveStudentsRequest(BaseModel):
#     student_ids: List[str]

# # Response model (optional, for clarity)
# class ListOfStudentsResponse(BaseModel):
#     id: str
#     studentList: List[dict]
#     noOfStudents: int
#     # Add other fields as needed

@app.delete("/lists/{list_id}/students", response_model=ListOfStudentsResponse)
# @app.delete("/lists/{list_id}/students", response_model=ListOfStudentsResponse)
def remove_students(
    list_id: str,
    request: RemoveStudentsRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Query the list
    db_list = db.query(ListOfStudents).filter(ListOfStudents.id == list_id).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    current_students = db_list.studentList or []
    # Filter out students with matching IDs
    updated_students = [s for s in current_students if s.get("studentId") not in request.student_ids]
    
    # Check if any students were removed (optional)
    if len(updated_students) == len(current_students):
        raise HTTPException(status_code=400, detail="No matching students found to remove")
    
    # Update the list
    db_list.studentList = updated_students
    db_list.noOfStudents = len(updated_students)
    # db_list.updatedAt = get_current_timestamp()  # Uncommented
    
    db.commit()
    db.refresh(db_list)
    return db_list











# import os
# import tempfile

# @app.get("/students/{list_id}/export")
# async def export_student_list_to_excel(list_id: str, db: Session = Depends(get_db)):
#     student_list_record = db.query(ListOfStudents).filter(ListOfStudents.id == list_id).first()
#     if not student_list_record:
#         raise HTTPException(status_code=404, detail="Student list not found")
    
#     # Extract student list data
#     student_list = student_list_record.studentList
    
#     # Convert to DataFrame
#     df = pd.DataFrame(student_list)
    
#     # Generate Excel file in temporary directory
#     temp_dir = tempfile.gettempdir()
#     excel_filename = os.path.join(temp_dir, f"student_list_{list_id}.xlsx")
#     df.to_excel(excel_filename, index=False)
    
#     # Return file response
#     return FileResponse(
#         path=excel_filename,
#         filename=f"student_list_{list_id}.xlsx",
#         media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )




@app.get("/download-list/{list_id}")
def download_list(list_id: str, db: Session = Depends(get_db)):
    student_list_record = db.query(ListOfStudents).filter(ListOfStudents.id == list_id).first()

    if not student_list_record:
        raise HTTPException(status_code=404, detail="Student list not found")

    student_data = student_list_record.studentList
    student_data_name = student_list_record.listName

    if not student_data or not isinstance(student_data, list):
        raise HTTPException(status_code=400, detail="No student data available in this list")

    df = pd.DataFrame(student_data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)

    # Use student_data_name as the filename, ensuring it's safe for use in headers
    safe_filename = f"{student_data_name}.xlsx".replace(" ", "_").replace("/", "_")
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={safe_filename}"
        }
    )



@app.post("/share-list")
def share_list(request: ShareListRequest, db: Session = Depends(get_db)):
    # Check if list exists
    original = db.query(ListOfStudents).filter(ListOfStudents.id == request.list_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Original list not found")

    shared_by_user = db.query(CmsUsers).filter(CmsUsers.id == request.shared_by).first()
    if not shared_by_user:
        raise HTTPException(status_code=404, detail="Shared-by user not found")

    successful_shares = []

    for shared_to in request.shared_to:
        # Check for duplicates
        existing = db.query(SharedListAccess).filter(
            SharedListAccess.listId == request.list_id,
            SharedListAccess.sharedWith == shared_to
        ).first()
        if existing:
            print("data already exist")
            continue  

        shared_with_user = db.query(CmsUsers).filter(CmsUsers.id == shared_to).first()
        if not shared_with_user:
            continue  
        shared = SharedListAccess(
            listId=request.list_id,
            sharedWith=shared_to,
            sharedBy=request.shared_by,
            sharedWithName=shared_with_user.fullName,
            sharedByName=shared_by_user.fullName
        )
        db.add(shared)
        successful_shares.append(shared_with_user.fullName)

    db.commit()

    if not successful_shares:
        raise HTTPException(status_code=400, detail="invalid.")

    return {
        "success": True,
        "message": f"List shared with: {', '.join(successful_shares)}"
    }


@app.get("/shared-list")
def share_list(
    list: str,
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    admin_user = db.query(CmsUsers).filter(CmsUsers.id == user_id).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin user not found")

    current_user_id = current_user["user_id"]

    users = db.query(
        CmsUsers.id,
        CmsUsers.fullName,
        exists().where(
            and_(
                SharedListAccess.sharedWith == CmsUsers.id,
                SharedListAccess.listId == list
            )
        ).label("shared")
    ).filter(
        or_(
            CmsUsers.parentId == admin_user.id, 
            CmsUsers.id == admin_user.id         
        )
    ).filter(CmsUsers.id != current_user_id).all()  

    result = [
        {
            "id": user.id,
            "fullName": user.fullName,
            "shared": user.shared
        } for user in users
    ]

    return result