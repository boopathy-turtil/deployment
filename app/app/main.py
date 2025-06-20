# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routers import employee, auth

# app = FastAPI(title="Employee CRUD API", version="1.0.0")

# # CORS configuration
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Adjust in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(employee.router, prefix="/employees", tags=["employees"])

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Employee CRUD API"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.staticfiles import StaticFiles

from .database import engine, Base
# from .models import User, Employee
# from .auth.router import router as auth_router
# from .employees.router import router as employee_router
from .apis.auth.auth import app as cms_auth_router
from .apis.college.college import app as cms_college_router
from .apis.placements.placements import app as cms_placements_router
from .apis.students.student import app as cms_student_router
from .apis.imageupload.imageupload import app as cms_imageupload_router
from .apis.listofstudents.listofstudents import app as cms_listofstudents_router
from .apis.dynamic.dynamic import app as cms_dynamic_router
from .apis.timeTable.api import app as cms_time_table
from .apis.attendence.api import app as cms_attendence
from .apis.result.api import app as cms_result
from .apis.assignment.api import app as cms_assignment



Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(auth_router)
# app.include_router(employee_router)
app.include_router(cms_auth_router)
app.include_router(cms_college_router)
app.include_router(cms_placements_router)
app.include_router(cms_student_router)
app.include_router(cms_imageupload_router)
app.include_router(cms_listofstudents_router)
app.include_router(cms_dynamic_router)
app.include_router(cms_time_table)
app.include_router(cms_attendence)
app.include_router(cms_result)
app.include_router(cms_assignment)

@app.get("/")
def read_root():
    return {"message": "Employee CRUD API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

