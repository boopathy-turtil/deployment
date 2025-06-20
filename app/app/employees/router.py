# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from ..models import User  # Add this import

# from ..database import get_db
# from ..models import Employee
# from ..schemas import EmployeeCreate, EmployeeUpdate, Employee

# from ..models import Employee as EmployeeModel
# from ..schemas import EmployeeCreate, EmployeeUpdate, Employee as EmployeeSchema

# from ..auth.security import get_current_user

# router = APIRouter(prefix="/employees", tags=["employees"])

# # @router.post("/", response_model=Employee)
# # def create_employee(
# #     employee: EmployeeCreate,
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user)
# # ):
# #     db_employee = db.query(Employee).filter(Employee.email == employee.email).first()
# #     if db_employee:
# #         raise HTTPException(status_code=400, detail="Email already registered")
# #     db_employee = Employee(**employee.model_dump())
# #     db.add(db_employee)
# #     db.commit()
# #     db.refresh(db_employee)
# #     return db_employee

# # @router.get("/", response_model=list[Employee])
# # def read_employees(
# #     skip: int = 0, 
# #     limit: int = 100,
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user)
# # ):
# #     employees = db.query(Employee).offset(skip).limit(limit).all()
# #     return employees

# # @router.get("/{employee_id}", response_model=Employee)
# # def read_employee(
# #     employee_id: int, 
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user)
# # ):
# #     employee = db.query(Employee).filter(Employee.id == employee_id).first()
# #     if not employee:
# #         raise HTTPException(status_code=404, detail="Employee not found")
# #     return employee

# # @router.put("/{employee_id}", response_model=Employee)
# # def update_employee(
# #     employee_id: int,
# #     employee: EmployeeUpdate,
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user)
# # ):
# #     db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
# #     if not db_employee:
# #         raise HTTPException(status_code=404, detail="Employee not found")
# #     for key, value in employee.model_dump().items():
# #         setattr(db_employee, key, value)
# #     db.commit()
# #     db.refresh(db_employee)
# #     return db_employee

# # @router.delete("/{employee_id}")
# # def delete_employee(
# #     employee_id: int,
# #     db: Session = Depends(get_db),
# #     current_user: User = Depends(get_current_user)
# # ):
# #     employee = db.query(Employee).filter(Employee.id == employee_id).first()
# #     if not employee:
# #         raise HTTPException(status_code=404, detail="Employee not found")
# #     db.delete(employee)
# #     db.commit()
# #     return {"message": "Employee deleted successfully"}


# @router.post("/", response_model=EmployeeSchema)
# def create_employee(
#     employee: EmployeeCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     db_employee = db.query(EmployeeModel).filter(EmployeeModel.email == employee.email).first()
#     if db_employee:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     db_employee = EmployeeModel(**employee.model_dump())
#     db.add(db_employee)
#     db.commit()
#     db.refresh(db_employee)
#     return db_employee



# @router.get("/", response_model=list[EmployeeSchema])
# def read_employees(
#     skip: int = 0, 
#     limit: int = 100,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     employees = db.query(EmployeeModel).offset(skip).limit(limit).all()
#     return employees

# @router.get("/{employee_id}", response_model=EmployeeSchema)
# def read_employee(
#     employee_id: int, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     return employee

# @router.put("/{employee_id}", response_model=EmployeeSchema)
# def update_employee(
#     employee_id: int,
#     employee: EmployeeUpdate,
#     db: Session = Depends(get_db),
#     # current_user: User = Depends(get_current_user)
# ):
#     db_employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
#     if not db_employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     for key, value in employee.model_dump().items():
#         setattr(db_employee, key, value)
#     db.commit()
#     db.refresh(db_employee)
#     return db_employee

# @router.delete("/{employee_id}")
# def delete_employee(
#     employee_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee not found")
#     db.delete(employee)
#     db.commit()
#     return {"message": "Employee deleted successfully"}

# # from fastapi import APIRouter, Depends, HTTPException, status
# # from sqlalchemy.orm import Session
# # from ..database import get_db
# # from ..models import Employee as EmployeeModel
# # from ..schemas import EmployeeCreate, EmployeeUpdate, Employee as EmployeeSchema

# # router = APIRouter(prefix="/employees", tags=["employees"])

# # @router.post("/", response_model=EmployeeSchema)
# # def create_employee(
# #     employee: EmployeeCreate,
# #     db: Session = Depends(get_db),
# # ):
# #     db_employee = db.query(EmployeeModel).filter(EmployeeModel.email == employee.email).first()
# #     if db_employee:
# #         raise HTTPException(status_code=400, detail="Email already registered")
# #     db_employee = EmployeeModel(**employee.model_dump())
# #     db.add(db_employee)
# #     db.commit()
# #     db.refresh(db_employee)
# #     return db_employee

# # @router.get("/", response_model=list[EmployeeSchema])
# # def read_employees(
# #     skip: int = 0, 
# #     limit: int = 100,
# #     db: Session = Depends(get_db),
# # ):
# #     employees = db.query(EmployeeModel).offset(skip).limit(limit).all()
# #     return employees

# # @router.get("/{employee_id}", response_model=EmployeeSchema)
# # def read_employee(
# #     employee_id: int, 
# #     db: Session = Depends(get_db),
# # ):
# #     employee = db.query(EmployeeModel).filter(EmployeeModel.id == employee_id).first()
# #     if not employee:
# #         raise HTTPException(status_code=404, detail="Employee not found")
# #     return employee
