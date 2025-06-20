from fastapi import APIRouter, UploadFile, File, HTTPException,Form,Depends
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from typing import List
from ... import  schemas, models
from ...models import Result,CollegeStudents,ExamMetadata,CmsUsers
from ...database import get_db
import zipfile
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from uuid import uuid4
from ...schemas import ExamUpdateRequest
from ...tokendecode import get_current_user

app = APIRouter(prefix="/cms-results", tags=["cms-results"])


from sqlalchemy import or_
from sqlalchemy import func, literal_column
from fastapi import HTTPException, UploadFile, File, Form, Depends
from io import BytesIO

import csv
from collections import defaultdict
from io import StringIO

def get_org_id_from_user_id(db: Session, user_id: str) -> str:
    user = db.query(CmsUsers).filter(CmsUsers.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    return user.parentId if user.parentId else user.id
@app.get("/get-exams/")
def get_exam_result( db: Session = Depends(get_db),current_user: dict = Depends(get_current_user)):
    org_id = get_org_id_from_user_id(db, current_user['user_id'])
    print(current_user['user_id'],"**************",org_id)
    result=db.query(ExamMetadata).filter(ExamMetadata.org_id==org_id).all()
    return result

@app.get("/get-results/")
def get_filtered_results(
    batch: int,
    degree: str,
    branch: str,
    exam_name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)

):
    results = db.query(Result).filter(
        Result.batch == batch,
        Result.degree == degree,
        Result.branch == branch,
        Result.examName == exam_name
    ).all()

    response_data = []
    for result in results:
        student = db.query(CollegeStudents).filter(CollegeStudents.studentId == result.studentId).first()
        student_name = student.studentName if student else "Unknown"
        student_row = {
            "Student ID": result.studentId,
            "Student Name": student_name,
        }

        student_row.update(result.subjectsDetails)

        student_row["OVERALL"] = f"{result.overall}%"
        student_row["STATUS"] = result.status

        response_data.append(student_row)

    return {
        "exam_name": exam_name,
        "degree": degree,
        "batch": batch,
        "branch": branch,
        "results": response_data
    }


@app.post("/upload_results/")
async def upload_results(
    examName: str ,
    degree: str ,
    branch: str ,
    batch: int ,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file format")

    org_id = get_org_id_from_user_id(db, current_user['user_id'])

    exam = db.query(ExamMetadata).filter_by(
        examName=examName, degree=degree, branch=branch, batch=batch, org_id=org_id
    ).first()

    if not exam:
        exam = ExamMetadata(
            id=str(uuid4()),
            examName=examName,
            degree=degree,
            branch=branch,
            batch=batch,
            publishedDate=None,
            status="Draft",
            org_id=org_id
        )
        db.add(exam)
        db.commit()
        db.refresh(exam)

    content = await file.read()
    csv_data = content.decode("utf-8")
    reader = csv.DictReader(StringIO(csv_data))

    rows = list(reader)
    duplicate_ids = []

    for row in rows:
        student_id = row["Student ID"].strip()
        existing_result = db.query(Result).filter_by(
            studentId=student_id,
            examId=exam.id
        ).first()
        if existing_result:
            duplicate_ids.append(student_id)

    if duplicate_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Duplicate result(s) found for student ID(s): {', '.join(duplicate_ids)}"
        )

    for row in rows:
        student_id = row["Student ID"].strip()
        student = db.query(CollegeStudents).filter(CollegeStudents.studentId == student_id).first()
        if not student:
            continue  

        subject_marks = {k: float(v) for k, v in row.items() if k.startswith("M-")}
        overall = round(sum(subject_marks.values()) / len(subject_marks), 2)
        status = "Pass" if all(m >= 40 for m in subject_marks.values()) else "Fail"

        result = Result(
            id=str(uuid4()),
            studentId=student_id,
            subjectsDetails=subject_marks,
            status=status,
            overall=overall,
            degree=degree,
            batch=batch,
            branch=branch,
            examName=examName,
            examId=exam.id,
            phone=student.phone
        )
        db.add(result)

    db.commit()
    return {"message": "Results uploaded successfully", "exam_id": exam.id}


@app.post("/update-exam/")
def update_exam_metadata(
    update_data: ExamUpdateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    
    org_id = get_org_id_from_user_id(db, current_user['user_id'])
    exam = db.query(ExamMetadata).filter(
        ExamMetadata.id == update_data.exam_id,
        ExamMetadata.org_id == org_id
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found or unauthorized")

    if update_data.publishedDate is not None:
        exam.publishedDate = update_data.publishedDate
    if update_data.status is not None:
        exam.status = update_data.status

    db.commit()
    db.refresh(exam)

    return {
        "message": "Exam updated successfully",
        "exam": {
            "id": exam.id,
            "examName": exam.examName,
            "publishedDate": exam.publishedDate,
            "status": exam.status
        }
    }


@app.delete("/delete-exam/")
def delete_exam(
    exam_id: str ,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    org_id = get_org_id_from_user_id(db, current_user['user_id'])
    exam = db.query(ExamMetadata).filter(
        ExamMetadata.id == exam_id,
        ExamMetadata.org_id == org_id
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    db.query(Result).filter(Result.examId == exam_id).delete()

    db.delete(exam)
    db.commit()

    return {"message": f"Exam '{exam.examName}' deleted successfully", "exam_id": exam_id}