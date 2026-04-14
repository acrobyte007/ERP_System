# feature/institute/schemas.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import re

class InstituteStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
    archived = "archived"

class AcademicModeEnum(str, Enum):
    year = "year"
    semester = "semester"

def validate_email_format(email: str) -> bool:
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pattern, email))

class InstituteBase(BaseModel):
    name: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    academic_structure: Optional[str] = None
    academic_mode: AcademicModeEnum

    @validator('email')
    def validate_email(cls, v):
        if v and not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v

class InstituteCreate(InstituteBase):
    status: InstituteStatusEnum = InstituteStatusEnum.active
    is_active: bool = True

class InstituteUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    code: Optional[str] = Field(None, min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    academic_structure: Optional[str] = None
    academic_mode: Optional[AcademicModeEnum] = None
    status: Optional[InstituteStatusEnum] = None
    is_active: Optional[bool] = None

    @validator('email')
    def validate_email(cls, v):
        if v and not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v

class InstituteStatusUpdate(BaseModel):
    status: InstituteStatusEnum

class InstituteResponse(InstituteBase):
    institute_id: int
    status: InstituteStatusEnum
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InstituteStatsResponse(BaseModel):
    total_students: int
    total_employees: int
    total_academic_years: int
    total_standards: int
    total_subjects: int
    total_hostels: int
    total_users: int
    active_enrollments: int
    current_academic_year: Optional[str] = None

    class Config:
        from_attributes = True