# feature/admin_auth/schemas.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import re

def validate_email_format(email: str) -> bool:
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone_format(phone: str) -> bool:
    pattern = r'^[0-9]{10}$'
    return bool(re.match(pattern, phone))

class AdminStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class AdminStatusEnum(str, Enum):
    pending = "pending"
    active = "active"
    suspended = "suspended"
    rejected = "rejected"

class SuperAdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    secret_key: str

    @validator('email')
    def validate_email(cls, v):
        if not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers and underscore')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_id: int
    username: str
    role: str

class InstituteAdminCreate(BaseModel):
    institute_id: int
    name: str = Field(..., min_length=2, max_length=100)
    email: str
    phone: str = Field(..., min_length=10, max_length=10)
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

    @validator('email')
    def validate_email(cls, v):
        if not validate_email_format(v):
            raise ValueError('Invalid email format')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not validate_phone_format(v):
            raise ValueError('Phone number must be 10 digits')
        return v

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers and underscore')
        return v

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class InstituteAdminResponse(BaseModel):
    admin_id: int
    institute_id: int
    name: str
    email: str
    phone: str
    username: str
    status: AdminStatusEnum
    created_at: datetime

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

    @validator('new_password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class AdminStatusUpdate(BaseModel):
    status: AdminStatusEnum