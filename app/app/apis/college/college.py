
# from pydantic import BaseModel
# from typing import List, Optional
# from uuid import UUID
# import json

# # Assuming Base and CollegeDegree are defined in models.py
# from .models import CollegeDegree, Base
# from .database import get_db  # Assuming you have a database dependency

# app = FastAPI()

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.future import select
from sqlalchemy import delete, update


import logging
from fastapi import APIRouter, Depends, HTTPException, status
from ...models import  CollegeDegree

from ...schemas import *
from ...database import get_db
from ...config import settings

from fastapi import Query




from ...tokendecode import get_current_user

from fastapi.security import OAuth2PasswordRequestForm




# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = APIRouter(prefix="/cms-college-degree", tags=["cms-college-degree"])


# Create a new college degree
@app.post("/collegedegree/", response_model=DegreeResponse)
async def add_college_degree(
    degree: DegreeCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Add auth if needed
    ):
    # Check if collegeId already exists
    existing_degree = db.execute(
        select(CollegeDegree).filter(CollegeDegree.collegeId == degree.collegeId)
    )
    if existing_degree.scalars().first():
        raise HTTPException(status_code=400, detail="College ID already exists")
    
    db_degree = CollegeDegree(
        collegeId=degree.collegeId,
        collegeShortName=degree.collegeShortName,
        degrees=degree.degrees
    )
    db.add(db_degree)
    db.commit()
    db.refresh(db_degree)
    return db_degree

# Update an existing college degree by collegeId
@app.put("/collegedegree/{college_id}", response_model=DegreeResponse)
async def update_college_degree(
    college_id: str, 
    degree: DegreeUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    result = db.execute(
        select(CollegeDegree).filter(CollegeDegree.collegeId == college_id)
    )
    db_degree = result.scalars().first()
    
    if not db_degree:
        raise HTTPException(status_code=404, detail="College degree not found")
    
    update_data = degree.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_degree, key, value)
    
    db.commit()
    db.refresh(db_degree)
    return db_degree

# Get college degree by collegeId
@app.get("/collegedegree/id/{college_id}", response_model=DegreeResponse)
async def get_college_degree_by_id(
    college_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    result = db.execute(
        select(CollegeDegree).filter(CollegeDegree.collegeId == college_id)
    )
    db_degree = result.scalars().first()
    
    if not db_degree:
        raise HTTPException(status_code=404, detail="College degree not found")
    
    return db_degree

# Get college degree by collegeShortName
@app.get("/collegedegree/shortname/{short_name}", response_model=DegreeResponse)
async def get_college_degree_by_shortname(
    short_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    result = db.execute(
        select(CollegeDegree).filter(CollegeDegree.collegeShortName == short_name)
    )
    db_degree = result.scalars().first()
    
    if not db_degree:
        raise HTTPException(status_code=404, detail="College degree not found")
    
    return db_degree

# Delete college degree by collegeId
@app.delete("/collegedegree/{college_id}")
async def delete_college_degree(
    college_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    result = db.execute(
        select(CollegeDegree).filter(CollegeDegree.collegeId == college_id)
    )
    db_degree = result.scalars().first()
    
    if not db_degree:
        raise HTTPException(status_code=404, detail="College degree not found")
    
    db.execute(
        delete(CollegeDegree).where(CollegeDegree.collegeId == college_id)
    )
    db.commit()
    return {"message": "College degree deleted successfully"}