from fastapi import HTTPException, Depends, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, JSON, Integer
from typing import Dict, Any
import logging
from uuid import uuid4
import time

from ...database import get_db, Base, engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = APIRouter(prefix="/dynamic", tags=["dynamic-crud"])

# Single dummy table model
class DummyTable(Base):
    __tablename__ = "dummy"
    
    path_key = Column(String, primary_key=True, index=True)
    data = Column(JSON, nullable=True, default={})
    createdAt = Column(Integer, default=lambda: int(time.time()))
    updatedAt = Column(Integer, onupdate=lambda: int(time.time()))

# Create the table
try:
    DummyTable.__table__.create(bind=engine, checkfirst=True)
except Exception as e:
    logger.error(f"Error creating dummy table: {e}")

@app.post("/{path_key}", status_code=status.HTTP_201_CREATED)
async def create_object(
    path_key: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create or update object with the specified path key"""
    try:
        # Check if record exists
        existing_record = db.query(DummyTable).filter(DummyTable.path_key == path_key).first()
        
        if existing_record:
            # Update existing record
            existing_record.data = data
            existing_record.updatedAt = int(time.time())
            db.commit()
            db.refresh(existing_record)
            return {
                "path_key": existing_record.path_key,
                "data": existing_record.data,
                "createdAt": existing_record.createdAt,
                "updatedAt": existing_record.updatedAt
            }
        else:
            # Create new record
            new_record = DummyTable(
                path_key=path_key,
                data=data
            )
            
            db.add(new_record)
            db.commit()
            db.refresh(new_record)
            
            return {
                "path_key": new_record.path_key,
                "data": new_record.data,
                "createdAt": new_record.createdAt,
                "updatedAt": new_record.updatedAt
            }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating/updating object with path_key {path_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating object: {str(e)}"
        )

@app.get("/{path_key}")
async def get_object(
    path_key: str,
    db: Session = Depends(get_db)
):
    """Get object with the specified path key"""
    try:
        # Query for the record
        record = db.query(DummyTable).filter(DummyTable.path_key == path_key).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object not found for path {path_key}"
            )
        
        return {
            "path_key": record.path_key,
            "data": record.data,
            "createdAt": record.createdAt,
            "updatedAt": record.updatedAt
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting object for path {path_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving object: {str(e)}"
        )

@app.put("/{path_key}")
async def update_object(
    path_key: str,
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update object with the specified path key"""
    try:
        # Query for the record
        record = db.query(DummyTable).filter(DummyTable.path_key == path_key).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object not found for path {path_key}"
            )
        
        # Update the record
        record.data = data
        record.updatedAt = int(time.time())
        
        db.commit()
        db.refresh(record)
        
        return {
            "path_key": record.path_key,
            "data": record.data,
            "createdAt": record.createdAt,
            "updatedAt": record.updatedAt
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating object for path {path_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating object: {str(e)}"
        )

@app.delete("/{path_key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(
    path_key: str,
    db: Session = Depends(get_db)
):
    """Delete object with the specified path key"""
    try:
        # Query for the record
        record = db.query(DummyTable).filter(DummyTable.path_key == path_key).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Object not found for path {path_key}"
            )
        
        # Delete the record
        db.delete(record)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting object for path {path_key}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting object: {str(e)}"
        )