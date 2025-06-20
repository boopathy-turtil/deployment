from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy import delete, update,  or_


import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ...models import CollegeStudents

from ...schemas import *
from ...database import get_db
from ...config import settings

from fastapi import Query
from sqlalchemy.orm import Session
from uuid import uuid4






from ...tokendecode import get_current_user

# from fastapi.security import OAuth2PasswordRequestForm




# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = APIRouter(prefix="/cms-college-students", tags=["cms-college-students"])




# CRUD endpoints
@app.post("/college-students", response_model=CollegeStudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student: CollegeStudentCreate,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_user)
):
    """
    Create a new college student record
    """
    existing_user = db.query(CollegeStudents).filter(CollegeStudents.studentId == student.studentId).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already registered with this studentId"
        )
    db_student = CollegeStudents(id=str(uuid4()), **student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student



# @app.get("/college-students", response_model=List[CollegeStudentResponse])
# @app.get("/college-students", response_model=PaginatedResponse)

# async def get_students(
#     college_id: str,
#     page: int = Query(1, ge=1),  # Default page is 1, must be >= 1
#     page_size: int = Query(10, ge=1, le=100),  # Default page_size is 10, max 100
#     degree: Optional[str] = Query(None),  # Optional filter
#     branch: Optional[str] = Query(None),  # Optional filter
#     batch: Optional[str] = Query(None),  # Optional filter
#     section: Optional[str] = Query(None),  # Optional filter
#     gender: Optional[str] = Query(None),  # Optional filter
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Get a paginated list of students for a given college, ordered by latest record first, with optional filters
#     """
#     offset = (page - 1) * page_size
#     query = db.query(CollegeStudents).filter(CollegeStudents.collegeId == college_id)

#     # Apply optional filters if provided
#     if degree:
#         query = query.filter(CollegeStudents.degree == degree)
#     if branch:
#         query = query.filter(CollegeStudents.branch == branch)
#     if batch:
#         query = query.filter(CollegeStudents.batch == batch)
#     if section:
#         query = query.filter(CollegeStudents.section == section)
#     if gender:
#         query = query.filter(CollegeStudents.gender == gender)

#     db_students = query.order_by(CollegeStudents.createdAt.desc()).offset(offset).limit(page_size).all()
    
#     if not db_students:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="No students found for the requested page with the given filters"
#         )
    
#     # return db_students
    

#     return PaginatedResponse(
#         total=offset,
#         page=page,
#         per_page=page_size,
#         items=db_students
#     )



@app.post("/filter-college-students", response_model=PaginatedResponse)
async def get_students(
    filters: StudentFilterRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a paginated list of students for a given college, ordered by latest record first, with optional list-based filters
    """
    # Validate page and page_size
    if filters.page < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page must be >= 1")
    if filters.page_size < 1 or filters.page_size > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page size must be between 1 and 100")

    offset = (filters.page - 1) * filters.page_size
    query = db.query(CollegeStudents).filter(CollegeStudents.collegeId == filters.collegeId)

    # Apply optional list-based filters if provided
    if filters.degrees:
        query = query.filter(CollegeStudents.degree.in_(filters.degrees))
    if filters.branches:
        query = query.filter(CollegeStudents.branch.in_(filters.branches))
    if filters.batches:
        query = query.filter(CollegeStudents.batch.in_(filters.batches))
    if filters.sections:
        query = query.filter(CollegeStudents.section.in_(filters.sections))
    if filters.genders:
        query = query.filter(CollegeStudents.gender.in_(filters.genders))

    total_count = query.count()
    db_students = query.order_by(CollegeStudents.createdAt.desc()).offset(offset).limit(filters.page_size).all()
    
    if not db_students:
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail="No students found for the requested page with the given filters"
        # )
        return PaginatedResponse(
            total=total_count,
            page=filters.page,
            per_page=filters.page_size,
            items=[]
    )

    return PaginatedResponse(
        total=total_count,
        page=filters.page,
        per_page=filters.page_size,
        items=db_students
    )

@app.get("/college-students/{student_id}", response_model=CollegeStudentResponse)
async def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific student by ID
    """
    db_student = db.query(CollegeStudents).filter(CollegeStudents.studentId == student_id).first()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return db_student

@app.put("/college-students/{student_id}", response_model=CollegeStudentResponse)
async def update_student(
    student_id: str,
    student: CollegeStudentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a specific student by ID
    """
    db_student = db.query(CollegeStudents).filter(CollegeStudents.studentId == student_id).first()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    for key, value in student.model_dump().items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student

@app.delete("/college-students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a specific student by ID
    """
    db_student = db.query(CollegeStudents).filter(CollegeStudents.studentId == student_id).first()
    
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    db.delete(db_student)
    db.commit()
    return None


# @app.get("/search-students", response_model=PaginatedResponse)
# async def search_students(
#     collegeId: Optional[str] = Query(None, description="Student ID to search for"),
#     studentName: Optional[str] = Query(None, description="Student name to search for"),
#     page: int = Query(1, ge=1, description="Page number, starting from 1"),
#     per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
#     db: Session = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
# ):
#     """
#     Search for college students by studentId or studentName with pagination.
#     At least one of studentId or studentName must be provided.
#     """
#     if not collegeId and not studentName:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="At least one of studentId or studentName must be provided"
#         )

#     query = db.query(CollegeStudents.collegeId==collegeId)
    
#     if collegeId:
#         query = query.filter(CollegeStudents.studentId.ilike(f"%{studentId}%")) 
#     if studentName:
#         query = query.filter(CollegeStudents.studentName.ilike(f"%{studentName}%"))
    
#     # Get total count for pagination
#     total = query.count()
    
#     # Apply pagination
#     offset = (page - 1) * per_page
#     students = query.offset(offset).limit(per_page).all()
    
#     if not students:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="No students found matching the criteria"
#         )
    
#     return PaginatedResponse(
#         total=total,
#         page=page,
#         per_page=per_page,
#         items=students
#     )





@app.get("/search-students", response_model=PaginatedResponse)
async def search_students(
    collegeId: Optional[str] = Query(None, description="college ID to search for"),
    search: Optional[str] = Query(None, description="Search query for student ID or name"),
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Search college students by student ID or name with pagination.
    Requires a search query parameter.
    """
    if not search:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be provided"
        )

    base_query = db.query(CollegeStudents).filter(
        CollegeStudents.collegeId == collegeId
    )
    
    # Search in both studentId and studentName fields using OR condition
    filtered_query = base_query.filter(
        or_(
            CollegeStudents.studentId.ilike(f"%{search}%"),
            CollegeStudents.studentName.ilike(f"%{search}%")
        )
    )
    
    total = filtered_query.count()
    
    offset = (page - 1) * per_page
    students = filtered_query.offset(offset).limit(per_page).all()
    
    if not students:
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND,
        #     detail="No students found matching the search criteria"
        # )
        return PaginatedResponse(
            total=total,
            page=page,
            per_page=per_page,
            items=[]
        )
    
    return PaginatedResponse(
        total=total,
        page=page,
        per_page=per_page,
        items=students
    )