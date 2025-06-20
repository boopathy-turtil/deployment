# from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
# from sqlalchemy.sql import func
# from app.database import Base

# class Employee(Base):
#     __tablename__ = "employees"

#     id = Column(Integer, primary_key=True, index=True)
#     first_name = Column(String, nullable=False)
#     last_name = Column(String, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     salary = Column(Float, nullable=False)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     is_active = Column(Boolean, default=True)

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON,Date,Float
from sqlalchemy.sql import func
import time
from datetime import datetime
from sqlalchemy import Time
from sqlalchemy.orm import relationship
import uuid

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    position = Column(String)
    salary = Column(Integer)



class CmsEmailOTP(Base):
    __tablename__ = "Cms_Email_OTP"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, default=None)
    email = Column(String, unique=True, index=True)
    expiry = Column(Integer, default=0)
    otp = Column(Integer, default=0)
   

def get_current_timestamp():
    return int(time.time()) # milliseconds  return int(time.time()*1000)
def get_datetime_timestamp():
    return datetime.utcnow()
class CmsUsers(Base):
    __tablename__ = "Cms_Users"
    
    id = Column(String, primary_key=True, index=True)
    fullName = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, default=None)
    collegeName = Column(String)
    role = Column(String)
    status = Column(String)
    parentId = Column(
        String, 
        ForeignKey("Cms_Users.id", ondelete="SET NULL"), 
        index=True,
        nullable=True,
        default=None
    )
    modelAccess = Column(JSON, nullable=True, default=[])  # List of JSON objects
    logo = Column(JSON, nullable=True, default=[]) # New column for list of strings
    collegeDetails = Column(JSON, nullable=True, default=[])  # List of JSON objects
    affilliatedUnversity = Column(JSON, nullable=True, default=[])  # List of JSON objects
    address = Column(JSON, nullable=True, default=[])  # List of JSON objects
    resultFormat = Column(JSON, nullable=True, default=[])  # List of JSON objects
    degree = Column(String)
    branch = Column(String)
    profilePic = Column(String)
    createdAt = Column(Integer, default=get_current_timestamp)
    updatedAt = Column(Integer, onupdate=get_current_timestamp)





class CollegeDegree(Base):
    __tablename__ = "collegedegree"

    id = Column(Integer, primary_key=True, index=True)
    collegeId = Column(String, unique=True, index=True)
    collegeShortName = Column(String, index=True)
    degrees = Column(JSON, nullable=True, default=[])




class CollegePlacements(Base):
    __tablename__ = "collegeplacements"

    id = Column(Integer, primary_key=True, index=True)
    collegeId = Column(String, index=True)
    collegeShortName = Column(String, index=True)
    collegeName = Column(String)
    placementDate = Column(Integer)
    degree = Column(String)
    company = Column(String)
    batch = Column(String)
    branch = Column(String)
    createdAt = Column(Integer, default=get_current_timestamp)
    updatedAt = Column(Integer, onupdate=get_current_timestamp)




class CollegeStudents(Base):
    __tablename__ = "collegestudents"

    id = Column(String, primary_key=True, index=True)
    # studentId = Column(String,primary_key=True, index=True)
    collegeId = Column(String, index=True)
    collegeShortName = Column(String, index=True)
    collegeName = Column(String)
    studentId = Column(String, unique=True, index=True)
    studentName = Column(String, index=True)
    degree = Column(String)
    batch = Column(String)
    branch = Column(String)
    section = Column(String)
    gender = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    createdAt = Column(Integer, default=get_current_timestamp)
    updatedAt = Column(Integer, onupdate=get_current_timestamp)



class ListOfStudents(Base):
    __tablename__ = "listofstudents"

    id = Column(String, primary_key=True, index=True)
    # studentId = Column(String,primary_key=True, index=True)
    listName = Column(String)
    studentList = Column(JSON, nullable=True, default=[])
    noOfStudents = Column(Integer)
    listCreatedBy = Column(String, index=True)
    createdAt = Column(Integer, default=get_current_timestamp)
    updatedAt = Column(Integer, onupdate=get_current_timestamp)
    

class TimeTable(Base):
    __tablename__ = "TimeTable"
    id = Column(Integer, primary_key=True, index=True)
    degree=Column(String, nullable=True)
    batch=Column(String, nullable=True)
    branch=Column(String, nullable=True)
    section=Column(String, nullable=True)
    days=Column(String, nullable=True)
    subject=Column(String, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)


class Student_Attendance(Base):
    __tablename__ = "student_attendance"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    subject = Column(String, nullable=False)
    batch = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    section = Column(String, nullable=False)
    studentId = Column(String, ForeignKey("collegestudents.studentId"), nullable=False)
    status =  Column(Boolean, default=True)  
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    createdAt = Column(DateTime, default=get_datetime_timestamp)
    updatedAt = Column(DateTime, onupdate=get_datetime_timestamp)

class SharedListAccess(Base):
    __tablename__ = "shared_list_access"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    listId = Column(String, ForeignKey("listofstudents.id"))
    sharedWith = Column(String, ForeignKey("Cms_Users.id"), nullable=False)
    sharedBy = Column(String, ForeignKey("Cms_Users.id"), nullable=False)
    sharedAt = Column(Integer, default=get_current_timestamp)

    sharedWithName = Column(String, nullable=True)
    sharedByName = Column(String, nullable=True)


class ExamMetadata(Base):
    __tablename__ = "exam_metadata"

    id = Column(String, primary_key=True, index=True)  # Keep as String
    examName = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    batch = Column(Integer, nullable=False)
    publishedDate = Column(DateTime, default=None, nullable=True)
    status = Column(String, default="Draft")
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, onupdate=func.now())
    org_id=Column(String, ForeignKey("Cms_Users.id"), nullable=False) 

class Result(Base):
    __tablename__ = "results"
    
    id = Column(String, primary_key=True, index=True)
    examId = Column(String, ForeignKey("exam_metadata.id"), nullable=False) 
    examName= Column(String) 
    degree = Column(String) 
    batch = Column(Integer) 
    branch = Column(String)
    studentId = Column(String, ForeignKey("collegestudents.studentId"), nullable=False)
    phone = Column(String, unique=True, index=True)
    subjectsDetails = Column(JSON) 
    overall = Column(Float)
    status = Column(String)
    date = Column(Date, default=func.now())  
   

class AssignmentDetails(Base):
    __tablename__ = "assignment"

    id = Column(String, primary_key=True, index=True)
    title=Column(String, nullable=True)
    description=Column(String, nullable=True)
    submission=Column(String, nullable=True)
    dueDate = Column(DateTime, default=None, nullable=True)
    marks = Column(Integer, nullable=True)
    branch = Column(String, nullable=False)
    batch = Column(Integer, nullable=False)
    section = Column(String, nullable=False)
    org_id=Column(String, ForeignKey("Cms_Users.id"), nullable=False) 
    degree = Column(String, nullable=False)
    created_on = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, onupdate=func.now())
    