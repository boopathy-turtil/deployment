from fastapi import FastAPI, HTTPException, Depends, status
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from ...schemas import create_timetable
from ...database import get_db
from ...models import TimeTable
app = APIRouter(prefix="/cms-timetable", tags=["cms-timetable"])

@app.post("/create_timetable")
async def create_timeslot(
    request: create_timetable,
    db: Session = Depends(get_db)
):
    try:
        if request.id:
            existing_entry = db.query(TimeTable).filter(TimeTable.id == request.id).first()

            if existing_entry:
                existing_entry.degree = request.degree
                existing_entry.batch = request.batch
                existing_entry.branch = request.branch
                existing_entry.section = request.section
                existing_entry.days = request.days
                existing_entry.subject = request.subject
                existing_entry.start_time = request.start_time
                existing_entry.end_time = request.end_time

                db.commit()
                db.refresh(existing_entry)

                return {
                     "success":True,
                    "message": "Timetable entry updated successfully",
                    "data": {
                        "id": existing_entry.id,
                        "subject": existing_entry.subject,
                        "time": f"{existing_entry.start_time} - {existing_entry.end_time}"
                    }
                }

        else:
            # Create new entry
            new_entry = TimeTable(
                degree=request.degree,
                batch=request.batch,
                branch=request.branch,
                section=request.section,
                days=request.days,
                subject=request.subject,
                start_time=request.start_time,
                end_time=request.end_time
            )

            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)

            return {
                 "success":True,
                "message": "Timetable entry created successfully",
                "data": {
                    "id": new_entry.id,
                    "subject": new_entry.subject,
                    "time": f"{new_entry.start_time} - {new_entry.end_time}"
                }
            }

    except Exception as e:
        db.rollback()
        return {
             "success":False,
            "error": str(e)
        }
    
@app.get("/get_timetable")
async def get_timetable(
    degree: str,
    batch: int,
    branch: str,
    section: str,
    db: Session = Depends(get_db)
):
    try:

        print("degree",degree,"batch",batch,type(batch),"branch",branch,"section",section)
        timetable_entries = db.query(TimeTable).filter(
            TimeTable.degree == degree,
            TimeTable.batch == str(batch),
            TimeTable.branch == branch,
            TimeTable.section == section
        ).all()

        return {
            "success":True,
            "message": "Timetable retrieved successfully",
            "count": len(timetable_entries),
            "data": [
                {
                    "id": entry.id,
                    "day": entry.days,
                    "subject": entry.subject,
                    "start_time": entry.start_time.strftime("%H:%M"),
                    "end_time": entry.end_time.strftime("%H:%M"),
                   
                }
                for entry in timetable_entries
            ]
        }

    except Exception as e:
        return {
            "success":False,
            "error": str(e)
        }
    


@app.delete("/delete_timetable/{id}")
async def delete_timetable(id: int, db: Session = Depends(get_db)):
    try:
        entry = db.query(TimeTable).filter(TimeTable.id == id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Timetable entry not found")

        db.delete(entry)
        db.commit()

        return {
            "success":True,
            "message": f"Timetable entry with ID {id} deleted successfully"
        }

    except Exception as e:
        db.rollback()
        return {
            "success":False,
            "error": str(e)
        }