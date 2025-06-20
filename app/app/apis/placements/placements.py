from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy import delete, update


import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ...models import CollegePlacements

from ...schemas import *
from ...database import get_db
from ...config import settings

from fastapi import Query
from sqlalchemy.orm import Session





from ...tokendecode import get_current_user

# from fastapi.security import OAuth2PasswordRequestForm




# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = APIRouter(prefix="/cms-college-placements", tags=["cms-college-placements"])


# # Create a new college degree
# @app.post("/collegedegree/", response_model=DegreeResponse)
# async def add_college_degree(
#     degree: DegreeCreate, 
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_user)  # Add auth if needed
#     ):
#     # Check if collegeId already exists
#     existing_degree = db.execute(
#         select(CollegeDegree).filter(CollegeDegree.collegeId == degree.collegeId)
#     )
#     if existing_degree.scalars().first():
#         raise HTTPException(status_code=400, detail="College ID already exists")
    
#     db_degree = CollegeDegree(
#         collegeId=degree.collegeId,
#         collegeShortName=degree.collegeShortName,
#         degrees=degree.degrees
#     )
#     db.add(db_degree)
#     db.commit()
#     db.refresh(db_degree)
#     return db_degree

# # Update an existing college degree by collegeId
# @app.put("/collegedegree/{college_id}", response_model=DegreeResponse)
# async def update_college_degree(
#     college_id: str, 
#     degree: DegreeUpdate, 
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
#     ):
#     result = db.execute(
#         select(CollegeDegree).filter(CollegeDegree.collegeId == college_id)
#     )
#     db_degree = result.scalars().first()
    
#     if not db_degree:
#         raise HTTPException(status_code=404, detail="College degree not found")
    
#     update_data = degree.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_degree, key, value)
    
#     db.commit()
#     db.refresh(db_degree)
#     return db_degree

# # Get college degree by collegeId
# @app.get("/collegedegree/id/{college_id}", response_model=DegreeResponse)
# async def get_college_degree_by_id(
#     college_id: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
#     ):
#     result = db.execute(
#         select(CollegeDegree).filter(CollegeDegree.collegeId == college_id)
#     )
#     db_degree = result.scalars().first()
    
#     if not db_degree:
#         raise HTTPException(status_code=404, detail="College degree not found")
    
#     return db_degree

# # Get college degree by collegeShortName
# @app.get("/collegedegree/shortname/{short_name}", response_model=DegreeResponse)
# async def get_college_degree_by_shortname(
#     short_name: str,
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
#     ):
#     result = db.execute(
#         select(CollegeDegree).filter(CollegeDegree.collegeShortName == short_name)
#     )
#     db_degree = result.scalars().first()
    
#     if not db_degree:
#         raise HTTPException(status_code=404, detail="College degree not found")
    
#     return db_degree

# # Delete college degree by collegeId
# @app.delete("/collegedegree/{college_id}")
# async def delete_college_degree(
#     college_id: str, 
#     db: AsyncSession = Depends(get_db),
#     current_user: dict = Depends(get_current_user)
#     ):
#     result = db.execute(
#         select(CollegeDegree).filter(CollegeDegree.collegeId == college_id)
#     )
#     db_degree = result.scalars().first()
    
#     if not db_degree:
#         raise HTTPException(status_code=404, detail="College degree not found")
    
#     db.execute(
#         delete(CollegeDegree).where(CollegeDegree.collegeId == college_id)
#     )
#     db.commit()
#     return {"message": "College degree deleted successfully"}






# CRUD APIs
@app.post("/collegeplacements/", response_model=CollegePlacementResponse)
async def add_college_placement(
    placement: CollegePlacementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    db_placement = CollegePlacements(**placement.model_dump())
    db.add(db_placement)
    db.commit()
    db.refresh(db_placement)
    return db_placement

@app.get("/collegeplacements/{id}", response_model=CollegePlacementResponse)
async def get_college_placement_by_college_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    placement = db.query(CollegePlacements).filter(CollegePlacements.id == id).first()
    if not placement:
        raise HTTPException(status_code=404, detail="Placement not found")
    return placement

@app.put("/collegeplacements/{id}", response_model=CollegePlacementResponse)
async def update_college_placement_by_college_id(
    id: int, 
    placement_update: CollegePlacementUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    placement = db.query(CollegePlacements).filter(CollegePlacements.id == id).first()
    if not placement:
        raise HTTPException(status_code=404, detail="Placement not found")
    for key, value in placement_update.model_dump(exclude_unset=True).items():
        setattr(placement, key, value)
    db.commit()
    db.refresh(placement)
    return placement

@app.delete("/collegeplacements/{id}")
async def delete_college_placement_by_college_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    placement = db.query(CollegePlacements).filter(CollegePlacements.id == id).first()
    if not placement:
        raise HTTPException(status_code=404, detail="Placement not found")
    db.delete(placement)
    db.commit()
    return {"message": "Placement deleted successfully"}



@app.get("/fetch-collegeplacements", response_model=List[CollegePlacementResponse])
async def get_users(
    college_id: str,
    page: int = Query(1, ge=1),  # Default page is 1, must be >= 1
    page_size: int = Query(10, ge=1, le=100),  # Default page_size is 10, max 100
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth if needed
):
    """
    Get a paginated list of users, ordered by latest record first
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Query users with pagination, ordered by created_at in descending order
    db_users = db.query(CollegePlacements).filter(CollegePlacements.collegeId == college_id).order_by(CollegePlacements.createdAt.desc()).offset(offset).limit(page_size).all()
    
    if not db_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found for the requested page"
        )
    
    return db_users