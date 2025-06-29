from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.db.database import get_db
from app.schemas import employee as employee_schema
from app.api.auth import get_current_user, get_current_admin
from app.core import security

router = APIRouter()

@router.post("/employees", response_model=employee_schema.Employee)
def add_employee(
    emp_data: employee_schema.EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_admin)
):
    if db.query(models.Employee).filter(models.Employee.email == emp_data.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    if db.query(models.Employee).filter(models.Employee.phone == emp_data.phone).first():
        raise HTTPException(status_code=400, detail="Phone already exists")

    hashed_password = security.get_password_hash(emp_data.password)

    new_employee = models.Employee(
        name=emp_data.name,
        email=emp_data.email,
        phone=emp_data.phone,
        password_hash=hashed_password,
        role=emp_data.role or "clerk"
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.patch("/employees/{employee_id}", response_model=employee_schema.Employee)
def update_employee(
    employee_id: int,
    updates: employee_schema.EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_admin),
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)
    return employee


@router.get("/employees", response_model=List[employee_schema.Employee])
def list_employees(
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    return db.query(models.Employee).all()

@router.get("/employees/{employee_id}", response_model=employee_schema.Employee)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_user)
):
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.delete("/employees/{employee_id}", status_code=204)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: models.Employee = Depends(get_current_admin)
):
    if current_user.id == employee_id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()
    return

