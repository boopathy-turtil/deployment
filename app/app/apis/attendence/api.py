from fastapi import APIRouter, Depends, HTTPException,File,UploadFile,Form,Request,Query,status
from typing import Optional

from sqlalchemy.orm import Session
from ...models import CollegeStudents,Student_Attendance,TimeTable
from ...database import get_db
from ...schemas import ManualAttendanceRequest,AttendanceUploadRequest
from datetime import datetime
from pydantic import BaseModel
from typing import List
import json
import pandas as pd
from io import BytesIO
from sqlalchemy import func, distinct
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import StreamingResponse
from fpdf import FPDF

app = APIRouter(prefix="/cms-attendence", tags=["cms-attendence"])
@app.post("/mark_attendance")
async def mark_attendance(
    request: ManualAttendanceRequest,
    db: Session = Depends(get_db)
):
    inserted, skipped = 0, 0
    day_name = request.date.strftime("%A")

    timetable_entry = db.query(TimeTable).filter(
        TimeTable.subject == request.subject,
        TimeTable.batch == request.batch,
        TimeTable.branch == request.branch,
        TimeTable.section == request.section,
        TimeTable.days == day_name,
        TimeTable.start_time == request.start_time,
        TimeTable.end_time == request.end_time
    ).first()

    if not timetable_entry:
        raise HTTPException(status_code=404, detail="No matching session in timetable for this subject + time.")

    for entry in request.attendance:
        try:
            existing = db.query(Student_Attendance).filter(
                Student_Attendance.date == request.date,
                Student_Attendance.subject == request.subject,
                Student_Attendance.studentId == entry.studentId,
                Student_Attendance.start_time == request.start_time,
                Student_Attendance.end_time == request.end_time
            ).first()

            if existing:
                skipped += 1
                continue

            attendance_record = Student_Attendance(
                studentId=entry.studentId,
                date=request.date,
                subject=request.subject,
                batch=request.batch,
                branch=request.branch,
                section=request.section,
                status=entry.status,
                start_time=request.start_time,
                end_time=request.end_time
            )

            db.add(attendance_record)
            inserted += 1

        except Exception:
            skipped += 1
            continue

    db.commit()

    return {
        "success": True,
        "message": "Attendance marked for the selected session.",
        "added": inserted,
        "skipped": skipped
    }
@app.post("/upload_attendance")
async def upload_attendance_excel(
    data: str = Form(...),  
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        request_data = AttendanceUploadRequest(**json.loads(data))  # parse JSON string to model

        content = await file.read()
        df = pd.read_excel(BytesIO(content))

        required_columns = {"studentId", "studentName", "status"}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail="Missing required columns: studentId, studentName, status")

        parsed_date = datetime.strptime(request_data.date, "%Y-%m-%d").date()
        inserted, skipped = 0, 0

        for _, row in df.iterrows():
            student_id = str(row["studentId"]).strip()
            status_str = str(row["status"]).strip().lower()
            is_present = status_str in ["present", "1", "yes", "true"]

            existing = db.query(Student_Attendance).filter(
                Student_Attendance.studentId == student_id,
                Student_Attendance.date == parsed_date,
                Student_Attendance.subject == request_data.subject
            ).first()

            if existing:
                skipped += 1
                continue

            attendance = Student_Attendance(
                studentId=student_id,
                date=parsed_date,
                subject=request_data.subject,
                batch=request_data.batch,
                branch=request_data.branch,
                section=request_data.section,
                status=is_present,
                start_time=request_data.start_time,
                end_time=request_data.end_time
            )

            db.add(attendance)
            inserted += 1

        db.commit()

        return {
            "success": True,
            "message": "Attendance file uploaded.",
            "inserted": inserted,
            "skipped": skipped
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

@app.get("/get_attendance")
async def get_attendance(
    subject: str,
    batch: int,
    branch: str,
    section: str,
    start_time: str,
    db: Session = Depends(get_db)
):
    try:
        records = db.query(Student_Attendance, CollegeStudents).join(
            CollegeStudents,
            Student_Attendance.studentId == CollegeStudents.studentId
        ).filter(
            Student_Attendance.subject == subject,
            Student_Attendance.batch == str(batch),
            Student_Attendance.branch == branch,
            Student_Attendance.section == section,
            Student_Attendance.start_time == start_time
        ).all()

        if not records:
            raise HTTPException(
                status_code=404,
                detail="No attendance records found."
            )

        return {
            "success": True,
            "data": [
                {
                    "student_id": attendance.studentId,
                    "student_name": student.studentName,
                    "student_status": "Present" if attendance.status else "Absent"
                }
                for attendance, student in records
            ]
        }

    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError as db_exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(db_exc)}"
        )

    except Exception as e:
        print("Unexpected error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )




from sqlalchemy import func, distinct
from sqlalchemy import String

@app.get("/attendance_percentage")
async def get_attendance_percentage(
    subject: str,
    batch: int,
    branch: str,
    section: str,
    db: Session = Depends(get_db)
):
    batch = str(batch)  

    total_classes = db.query(
        func.count(
            distinct(
                func.concat(
                    Student_Attendance.date, 
                    func.cast(Student_Attendance.start_time, String),
                    func.cast(Student_Attendance.end_time, String)
                )
            )
        )
    ).filter(
        Student_Attendance.subject == subject,
        Student_Attendance.batch == batch,
        Student_Attendance.branch == branch,
        Student_Attendance.section == section
    ).scalar()


    # Get list of students
    students = db.query(CollegeStudents).filter(
        CollegeStudents.batch == batch,
        CollegeStudents.branch == branch,
        CollegeStudents.section == section
    ).all()

    data = []
    for student in students:
        present_classes = db.query(
            func.count(
                distinct(
                    func.concat(
                        Student_Attendance.date,
                        func.cast(Student_Attendance.start_time, String),
                        func.cast(Student_Attendance.end_time, String)
                    )
                )
            )
        ).filter(
            Student_Attendance.subject == subject,
            Student_Attendance.batch == batch,
            Student_Attendance.branch == branch,
            Student_Attendance.section == section,
            Student_Attendance.studentId == student.studentId,
            Student_Attendance.status == True
        ).scalar()

        percent = round((present_classes / total_classes) * 100, 2) if total_classes > 0 else 0

        data.append({
            "student_id": student.studentId,
            "student_name": student.studentName,
            "batch":student.batch,
            "branch":student.branch,
            "section":student.section,
            "attendance_percent": f"{percent}%"  

        })

    return {
        "success": True,
        "total_classes": total_classes,
        "data": data
    }





@app.post("/make_attendance")
async def mark_or_upload_attendance(
    date: str = Form(...),
    subject: str = Form(...),
    batch: str = Form(...),
    branch: str = Form(...),
    section: str = Form(...),
    start_time: str = Form(...),
    end_time: str = Form(...),
    attendance: Optional[str] = Form(None), 
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    try:
        print("*****************",file)
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
        inserted, skipped = 0, 0

        # Get day name from date
        day_name = parsed_date.strftime("%A")

        # Validate timetable
        timetable_entry = db.query(TimeTable).filter(
            TimeTable.subject == subject,
            TimeTable.batch == batch,
            TimeTable.branch == branch,
            TimeTable.section == section,
            TimeTable.days == day_name,
            TimeTable.start_time == start_time,
            TimeTable.end_time == end_time
        ).first()

        if not timetable_entry:
            raise HTTPException(status_code=404, detail="No matching session in timetable for this subject + time.")

        # If file is uploaded (Excel path)
        if file is not None:
            content = await file.read()
            df = pd.read_excel(BytesIO(content))

            required_columns = {"studentId", "studentName", "status"}
            if not required_columns.issubset(df.columns):
                raise HTTPException(status_code=400, detail="Missing required columns: studentId, studentName, status")

            for _, row in df.iterrows():
                student_id = str(row["studentId"]).strip()
                status_str = str(row["status"]).strip().lower()
                is_present = status_str in ["present", "1", "yes", "true"]

                existing = db.query(Student_Attendance).filter(
                    Student_Attendance.studentId == student_id,
                    Student_Attendance.date == parsed_date,
                    Student_Attendance.subject == subject,
                    Student_Attendance.start_time == start_time,
                    Student_Attendance.end_time == end_time
                ).first()

                if existing:
                    skipped += 1
                    continue

                db.add(Student_Attendance(
                    studentId=student_id,
                    date=parsed_date,
                    subject=subject,
                    batch=batch,
                    branch=branch,
                    section=section,
                    status=is_present,
                    start_time=start_time,
                    end_time=end_time
                ))
                inserted += 1

        # Else parse attendance JSON string (manual mode)
        elif attendance:
            attendance_list = json.loads(attendance)
            for entry in attendance_list:
                student_id = entry["studentId"]
                status = entry["status"]

                existing = db.query(Student_Attendance).filter(
                    Student_Attendance.studentId == student_id,
                    Student_Attendance.date == parsed_date,
                    Student_Attendance.subject == subject,
                    Student_Attendance.start_time == start_time,
                    Student_Attendance.end_time == end_time
                ).first()

                if existing:
                    existing.status = status
                    db.add(existing)
                    skipped += 1
                    continue

                db.add(Student_Attendance(
                    studentId=student_id,
                    date=parsed_date,
                    subject=subject,
                    batch=batch,
                    branch=branch,
                    section=section,
                    status=status,
                    start_time=start_time,
                    end_time=end_time
                ))
                inserted += 1
        else:
            raise HTTPException(status_code=400, detail="Either attendance JSON or Excel file must be provided.")

        db.commit()

        return {
            "success": True,
            "message": "Attendance processed successfully.",
            "inserted": inserted,
            "skipped": skipped
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")

@app.get("/overall_attendance_percentage")
async def get_true_overall_attendance_percentage(
    db: Session = Depends(get_db)
):
    total_sessions = db.query(
    func.count(
        distinct(
            func.concat(
                Student_Attendance.date,
                func.cast(Student_Attendance.start_time, String),
                func.cast(Student_Attendance.end_time, String)
            )
        )
    )
).scalar()

    if total_sessions == 0:
        return {
            "success": False,
            "message": "No session data available",
            "overall_attendance_percent": "0.00%"
        }

    students = db.query(distinct(Student_Attendance.studentId)).all()
    student_ids = [s[0] for s in students]
    total_students = len(student_ids)

    total_present = 0
    low_attendance_students = 0

    for student_id in student_ids:
        student_present = db.query(
            func.count(
                distinct(
                    func.concat(
                        Student_Attendance.date,
                        func.cast(Student_Attendance.start_time, String),
                        func.cast(Student_Attendance.end_time, String)
                    )
                )
            )
        ).filter(
            Student_Attendance.studentId == student_id,
            Student_Attendance.status == True
        ).scalar()

        percent = (student_present / total_sessions) * 100
        total_present += student_present

        if percent < 70:
            low_attendance_students += 1

    total_expected = total_students * total_sessions
    overall_percent = round((total_present / total_expected) * 100, 2)

    return {
        "success": True,
        "total_students": total_students,
        "total_sessions": total_sessions,
        "total_present": total_present,
        "total_expected": total_expected,
        "overall_attendance_percent": f"{overall_percent}%",
        "students_low_attendence": low_attendance_students
    }

from collections import defaultdict

@app.get("/generate_attendance_report")
async def generate_attendance_report(
    degree: str,
    batch: str,
    branch: str,
    section: str,
    from_date: str = Query(..., description="Format: YYYY-MM-DD"),
    to_date: str = Query(..., description="Format: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    try:
        start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        # Get list of students in filter
        students = db.query(CollegeStudents).filter(
            CollegeStudents.degree == degree,
            CollegeStudents.batch == batch,
            CollegeStudents.branch == branch,
            CollegeStudents.section == section
        ).all()

        if not students:
            raise HTTPException(status_code=404, detail="No students found for the given filters.")

        # Fetch all attendance records in range
        attendance_records = db.query(Student_Attendance).filter(
            Student_Attendance.date.between(start_date, end_date),
            Student_Attendance.batch == batch,
            Student_Attendance.branch == branch,
            Student_Attendance.section == section
        ).all()

        # Organize by student
        summary = defaultdict(lambda: {"presents": 0, "absents": 0, "total": 0})

        for record in attendance_records:
            sid = record.studentId
            summary[sid]["total"] += 1
            if record.status:
                summary[sid]["presents"] += 1
            else:
                summary[sid]["absents"] += 1

        # Build report
        report = []
        for student in students:
            sid = student.studentId
            name = student.studentName
            total = summary[sid]["total"]
            present = summary[sid]["presents"]
            absent = summary[sid]["absents"]
            percent = round((present / total) * 100, 2) if total > 0 else 0.0

            report.append({
                "Student ID": sid,
                "Name": name,
                "Batch": batch,
                "Branch": branch,
                "Section": section,
                "Total Sessions": total,
                "Presents": present,
                "Absents": absent,
                "Attendance %": f"{percent}%"
            })

        return {
            "success": True,
            "filters": {
                "degree": degree,
                "batch": batch,
                "branch": branch,
                "section": section,
                "from_date": from_date,
                "to_date": to_date
            },
            "data": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    


@app.get("/generate_attendance_report_pdf1")
async def generate_attendance_report_pdf(
    degree: str,
    batch: str,
    branch: str,
    section: str,
    from_date: str = Query(..., description="Format: YYYY-MM-DD"),
    to_date: str = Query(..., description="Format: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    try:
        start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        students = db.query(CollegeStudents).filter(
            CollegeStudents.degree == degree,
            CollegeStudents.batch == batch,
            CollegeStudents.branch == branch,
            CollegeStudents.section == section
        ).all()

        if not students:
            raise HTTPException(status_code=404, detail="No students found for the given filters.")

        attendance_records = db.query(Student_Attendance).filter(
            Student_Attendance.date.between(start_date, end_date),
            Student_Attendance.batch == batch,
            Student_Attendance.branch == branch,
            Student_Attendance.section == section
        ).all()

        summary = defaultdict(lambda: {"presents": 0, "absents": 0, "total": 0})

        for record in attendance_records:
            sid = record.studentId
            summary[sid]["total"] += 1
            if record.status:
                summary[sid]["presents"] += 1
            else:
                summary[sid]["absents"] += 1

        # Prepare rows
        report_rows = []
        for student in students:
            sid = student.studentId
            name = student.studentName
            total = summary[sid]["total"]
            present = summary[sid]["presents"]
            absent = summary[sid]["absents"]
            percent = round((present / total) * 100, 2) if total > 0 else 0.0

            report_rows.append({
                "Student ID": sid,
                "Name": name,
                "Batch": batch,
                "Branch": branch,
                "Section": section,
                "Total Sessions": total,
                "Presents": present,
                "Absents": absent,
                "Attendance %": f"{percent}%"
            })

        # Generate PDF using FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Attendance Report ({from_date} to {to_date})", ln=True, align="C")

        headers = list(report_rows[0].keys()) if report_rows else []
        col_width = pdf.w / len(headers) - 2 if headers else 30

        pdf.set_font("Arial", "B", 10)
        for header in headers:
            pdf.cell(col_width, 10, header, border=1, align="C")
        pdf.ln()

        pdf.set_font("Arial", "", 10)
        for row in report_rows:
            for value in row.values():
                pdf.cell(col_width, 10, str(value), border=1, align="C")
            pdf.ln()

        # Stream PDF
        pdf_bytes = pdf.output(dest="S").encode("latin1")
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)

        filename = f"attendance_report_{batch}_{branch}_{section}.pdf"
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {str(e)}")


@app.get("/generate_attendance_report_pdf")
async def generate_attendance_report_pdf(
    degree: str,
    batch: str,
    branch: str,
    section: str,
    from_date: str = Query(..., description="Format: YYYY-MM-DD"),
    to_date: str = Query(..., description="Format: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    try:
        # Parse dates
        start_date = datetime.strptime(from_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(to_date, "%Y-%m-%d").date()

        # Fetch students
        students = db.query(CollegeStudents).filter(
            CollegeStudents.degree == degree,
            CollegeStudents.batch == batch,
            CollegeStudents.branch == branch,
            CollegeStudents.section == section
        ).all()

        if not students:
            raise HTTPException(status_code=404, detail="No students found for the given filters.")

        # Fetch attendance
        attendance_records = db.query(Student_Attendance).filter(
            Student_Attendance.date.between(start_date, end_date),
            Student_Attendance.batch == batch,
            Student_Attendance.branch == branch,
            Student_Attendance.section == section
        ).all()

        # Summarize
        summary = defaultdict(lambda: {"presents": 0, "absents": 0, "total": 0})
        for record in attendance_records:
            sid = record.studentId
            summary[sid]["total"] += 1
            summary[sid]["presents"] += 1 if record.status else 0
            summary[sid]["absents"] += 0 if record.status else 1
            summary[sid]["subject"]=record.subject

        # Build report data
        report_rows = []
        for student in students:
            sid = student.studentId
            name = student.studentName
            subject=summary[sid]["subject"]
            total = summary[sid]["total"]
            present = summary[sid]["presents"]
            absent = summary[sid]["absents"]
            percent = round((present / total) * 100, 2) if total > 0 else 0.0

            report_rows.append({
                "Student ID": sid,
                "Name": name,
                "Batch": batch,
                "Branch": branch,
                "Section": section,
                "subject":subject,
                "No.of.Class": total,
                "Presents": present,
                "Absents": absent,
                " %": f"{percent}%"
            })

        pdf = FPDF(orientation="L", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)  
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        column_widths = {
            "Student ID": 25,
            "Name": 45,
            "Batch": 25,
            "Branch": 25,
            "Section": 20,
            "subject":40,
            "No.of.Class": 25,
            "Presents": 25,
            "Absents": 25,
            " %": 25
        }

        headers = list(column_widths.keys())

        # Table headers
        pdf.set_font("Arial", "B", 10)
        for header in headers:
            pdf.cell(column_widths[header], 10, header, border=1, align="C")
        pdf.ln()

        # Table rows
        pdf.set_font("Arial", "", 10)
        for row in report_rows:
            for key in headers:
                pdf.cell(column_widths[key], 10, str(row[key]), border=1, align="C")
            pdf.ln()

        pdf_bytes = pdf.output(dest="S").encode("latin1")
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)

        filename = f"attendance_report_{batch}_{branch}_{section}.pdf"
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF report: {str(e)}")