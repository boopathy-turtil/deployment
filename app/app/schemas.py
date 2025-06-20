# from pydantic import BaseModel, EmailStr
# from datetime import datetime
# from typing import Optional

# class EmployeeBase(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     salary: float

# class EmployeeCreate(EmployeeBase):
#     pass

# class EmployeeUpdate(EmployeeBase):
#     pass

# class Employee(EmployeeBase):
#     id: int
#     created_at: datetime
#     updated_at: Optional[datetime]

#     class Config:
#         from_attributes = True

# class UserBase(BaseModel):
#     username: str

# class UserCreate(UserBase):
#     password: str

# class User(UserBase):
#     id: int
#     is_active: bool

#     class Config:
#         from_attributes = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     username: Optional[str] = None

# from pydantic import BaseModel, EmailStr, ConfigDict
# from datetime import datetime
# from typing import List, Dict, Optional, Any


# # /app/app/schemas.py
# from pydantic import BaseModel

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     # email: str | None = None
#     email: Optional[str] = None

# class UserBase(BaseModel):
#     email: EmailStr

# class UserCreate(UserBase):
#     password: str

# class User(UserBase):
#     id: int
#     is_active: bool

#     class Config:
#         from_attributes = True

# class EmployeeBase(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     department: str
#     position: str
#     salary: int

# class EmployeeCreate(EmployeeBase):
#     pass

# class EmployeeUpdate(EmployeeBase):
#     pass

# class Employee(EmployeeBase):
#     id: int

#     class Config:
#         from_attributes = True



from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime,date
from typing import List, Dict, Optional, Any


# Pydantic models for request/response
class SendEmailRequest(BaseModel):
    # phoneNumber: str
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    # phoneNumber: str
    email: EmailStr
    otp: int
    # userId: int

class EmailResponse(BaseModel):
    message: str
    success: bool

class VerifyResponse(BaseModel):
    message: str
    success: bool
    verified: bool




# from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    fullName: Optional[str] = None
    phone: Optional[str] = None
    collegeName: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    parentId: Optional[str] = None
    degree : Optional[str] = None
    branch : Optional[str] = None
    profilePic : Optional[str] = None
    modelAccess: Optional[List[Dict]] = []
    logo: Optional[List[str]] = []
    collegeDetails: Optional[List[Dict]] = []
    affilliatedUnversity: Optional[List[Dict]] = []
    address: Optional[List[Dict]] = []
    resultFormat: Optional[List[Dict]] = []

class UserCreateResponse(BaseModel):
    message: str
    cmsUserId: str
    userName: str
    temparyPassword: str






# from typing import List, Dict, Optional, Any
# from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    cmsUserId: str
    role: str

class UserBase(BaseModel):
    email: str
    fullName: Optional[str] = None
    phone: Optional[str] = None
    collegeName: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    parentId: Optional[str] = None
    degree : Optional[str] = None
    branch : Optional[str] = None
    profilePic : Optional[str] = None
    modelAccess: Optional[List[Dict[str, Any]]] = []
    logo: Optional[List[str]] = []
    collegeDetails: Optional[List[Dict[str, Any]]] = []
    affilliatedUnversity: Optional[List[Dict[str, Any]]] = []
    address: Optional[List[Dict[str, Any]]] = []
    resultFormat: Optional[List[Dict[str, Any]]] = []

class UserCreate(UserBase):
    # password: str
    pass
    # email: str
    # fullName: Optional[str] = None
    # phone: Optional[str] = None
    # collegeName: Optional[str] = None
    # role: Optional[str] = None
    # status: Optional[str] = None

class UserUpdate(UserBase):
    pass  # All fields optional for update

class UserResponse(UserBase):
    id: str
    createdAt: int
    updatedAt: Optional[int] = None

    # Pydantic V2 config
    model_config = ConfigDict(from_attributes=True)




# Pydantic model for request
class ChangePasswordRequest(BaseModel):
    email: str
    oldPassword: str
    newPassword: str



# Pydantic model for request
class LoginRequest(BaseModel):
    userName: str
    Password: str
    


class FetchUserResponse(UserBase):
    id: str
    createdAt: int
    updatedAt: Optional[int] = None
    # parentId: Optional[str] = None
    parentId: str


    # Pydantic V2 config
    model_config = ConfigDict(from_attributes=True)





# Pydantic models for request/response
class DegreeCreate(BaseModel):
    collegeId: str
    collegeShortName: str
    degrees: Optional[List[Dict[str, Any]]] = []

class DegreeUpdate(BaseModel):
    collegeId: Optional[str] = None
    collegeShortName: Optional[str] = None
    degrees: Optional[List[Dict[str, Any]]] = []

class DegreeResponse(BaseModel):
    id: int
    collegeId: str
    collegeShortName: str
    degrees: Optional[List[Dict[str, Any]]] = []






# Pydantic Models
class CollegePlacementCreate(BaseModel):
    collegeId: str
    collegeShortName: str
    collegeName: str
    placementDate: int
    degree: str
    company: str
    batch: str
    branch: str

    model_config = ConfigDict(from_attributes=True)

class CollegePlacementUpdate(BaseModel):
    collegeShortName: Optional[str] = None
    collegeName: Optional[str] = None
    placementDate: Optional[int] = None
    degree: Optional[str] = None
    company: Optional[str] = None
    batch: Optional[str] = None
    branch: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class CollegePlacementResponse(BaseModel):
    id: int
    collegeId: str
    collegeShortName: str
    collegeName: str
    placementDate: int
    degree: str
    company: str
    batch: str
    branch: str
    createdAt: int
    updatedAt: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)






# Pydantic models for request/response
class CollegeStudentBase(BaseModel):
    collegeId: str
    collegeShortName: str
    collegeName: str
    studentId: str
    studentName: str
    email: str
    phone: str
    degree: str
    batch: str
    branch: str
    section: str
    gender: str

class CollegeStudentCreate(CollegeStudentBase):
    pass

class CollegeStudentUpdate(CollegeStudentBase):
    pass

class CollegeStudentResponse(CollegeStudentBase):
    id: str
    createdAt: int
    updatedAt: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)




class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: list[CollegeStudentResponse]



# class PaginatedResponse(BaseModel):
#     total: int
#     page: int
#     per_page: int
#     items: List[dict]

class StudentFilterRequest(BaseModel):
    collegeId: str
    degrees: Optional[List[str]] = None
    branches: Optional[List[str]] = None
    batches: Optional[List[str]] = None
    sections: Optional[List[str]] = None
    genders: Optional[List[str]] = None
    page: int = 1
    page_size: int = 10


# Pydantic model for request validation
class PresignedUrlRequest(BaseModel):
    file_name: str

# Pydantic model for response
class PresignedUrlResponse(BaseModel):
    statusCode: int
    message: str
    body: Optional[dict] = None




# class Student(BaseModel):
#     studentId: str
#     name: Optional[str] = None
    # Add other student fields as needed

class ListOfStudentsCreate(BaseModel):
    listName: str
    listCreatedBy: str
    studentList: Optional[List[CollegeStudentBase]] = []
    # noOfStudents: Optional[int] = 0

class ListOfStudentsUpdate(BaseModel):
    listName: Optional[str] = None
    listCreatedBy: Optional[str] = None
    studentList: Optional[List[CollegeStudentBase]] = None
    noOfStudents: Optional[int] = None

class ListOfStudentsResponse(BaseModel):
    id: str
    listName: str
    listCreatedBy: str
    studentList: List[CollegeStudentBase]
    noOfStudents: int
    createdAt: int
    updatedAt: Optional[int] = None
    shared: bool = False
    model_config = ConfigDict(from_attributes=True)




# Request body model
class RemoveStudentsRequest(BaseModel):
    student_ids: List[str]

# # Response model (optional, for clarity)
# class ListOfStudentsResponse(BaseModel):
#     id: str
#     studentList: List[dict]
#     noOfStudents: int
#     # Add other fields as needed
from datetime import time


class create_timetable(BaseModel):
    id: Optional[int] = None
    degree: str
    batch: int
    branch: str
    section: str
    days: str
    subject: str
    start_time: time
    end_time: time    


class StudentAttendance(BaseModel):
    studentId: str
    status: bool  # True = Present, False = Absent

class ManualAttendanceRequest(BaseModel):
    date: date
    subject: str
    batch: str
    branch: str
    section: str
    attendance: List[StudentAttendance]
    start_time: str
    end_time: str

class AttendanceUploadRequest(BaseModel):
    batch: str
    branch: str
    section: str
    subject: str
    date: str
    start_time: str
    end_time: str

class ShareListRequest(BaseModel):
    list_id: str
    shared_by: str
    shared_to: List[str] 

class ListContainerResponse(BaseModel):
    created_lists: List[ListOfStudentsResponse]
    shared_lists: List[ListOfStudentsResponse]

class SubjectMarksDetails(BaseModel):
    subject: str
    marks: float
    status: str
class ResultBase(BaseModel):
    student_id: str
    status: str  # "Pass" or "Fail"
    subjects_marks_details: List[SubjectMarksDetails]
    date: Optional[date] = None

class ExamUpdateRequest(BaseModel):
    exam_id: str
    publishedDate: Optional[datetime] = None
    status: Optional[str] = None