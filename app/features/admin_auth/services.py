# feature/admin_auth/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.admin_auth.repository import AdminAuthRepository
from app.features.admin_auth.schemas import (
    SuperAdminCreate, InstituteAdminCreate, AdminLoginRequest,
    ChangePasswordRequest, AdminStatusUpdate,AdminStatusEnum
)
from typing import Optional, List, Dict, Any
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 480
SUPER_ADMIN_SECRET = os.getenv("SUPER_ADMIN")

class AdminAuthService:
    def __init__(self, db: AsyncSession):
        self.repository = AdminAuthRepository(db)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def create_super_admin(self, admin_data: SuperAdminCreate) -> Dict[str, Any]:
        if admin_data.secret_key != SUPER_ADMIN_SECRET:
            return {"error": "Invalid secret key"}
        
        existing = await self.repository.get_user_by_username(admin_data.username)
        if existing:
            return {"error": "Username already exists"}
        
        user_dict = {
            "username": admin_data.username,
            "email":admin_data.email,
            "password_hash": self.hash_password(admin_data.password),
            "is_active": True
        }
        
        user = await self.repository.create_user(user_dict)
        
        super_admin_role = await self.repository.get_role_by_name("Super Admin")
        if not super_admin_role:
            role_dict = {
                "name": "Super Admin",
                "description": "Super Administrator with full system access"
            }
            super_admin_role = await self.repository.create_role(role_dict)
        
        await self.repository.assign_role_to_user(user.user_id, super_admin_role.role_id)
        
        return {
            "admin_id": user.user_id,
            "username": user.username,
            "role": "Super Admin",
            "message": "Super admin created successfully"
        }

    async def create_institute_admin(self, admin_data: InstituteAdminCreate) -> Dict[str, Any]:
        existing = await self.repository.get_user_by_username(admin_data.username)
        if existing:
            return {"error": "Username already exists"}
        
        institute = await self.repository.get_institute_by_id(admin_data.institute_id)
        if not institute:
            return {"error": "Institute not found"}
        
        employee_dict = {
            "institute_id": admin_data.institute_id,
            "name": admin_data.name,
            "email": admin_data.email,
            "phone": admin_data.phone,
            "joining_date": datetime.now().date(),
            "status": "active",
            "employee_code": f"ADMIN{admin_data.institute_id}_{datetime.now().timestamp()}",
            "designation": "Institute Administrator",
            "is_active": True
        }
        
        employee = await self.repository.create_employee(employee_dict)
        
        user_dict = {
            "institute_id": admin_data.institute_id,
            "username": admin_data.username,
            "password_hash": self.hash_password(admin_data.password),
            "employee_id": employee.employee_id,
            "is_active": True
        }
        
        user = await self.repository.create_user(user_dict)
        
        institute_admin_role = await self.repository.get_role_by_name("Institute Admin", admin_data.institute_id)
        if not institute_admin_role:
            role_dict = {
                "institute_id": admin_data.institute_id,
                "name": "Institute Admin",
                "description": "Institute Administrator with full access to institute"
            }
            institute_admin_role = await self.repository.create_role(role_dict)
        
        await self.repository.assign_role_to_user(user.user_id, institute_admin_role.role_id)
        
        return {
            "admin_id": user.user_id,
            "institute_id": admin_data.institute_id,
            "username": user.username,
            "role": "Institute Admin",
            "message": "Institute admin created successfully"
        }

    async def login(self, login_data: AdminLoginRequest) -> Optional[Dict[str, Any]]:
        user = await self.repository.get_user_by_username(login_data.username)
        if not user or not self.verify_password(login_data.password, user.password_hash):
            return None
        
        if not user.is_active:
            return None
        
        roles = await self.repository.get_user_roles(user.user_id)
        role_names = [r.name for r in roles]
        
        if "Super Admin" not in role_names and "Institute Admin" not in role_names:
            return None
        
        access_token = self.create_access_token(
            data={
                "sub": user.username,
                "user_id": user.user_id,
                "roles": role_names,
                "institute_id": user.institute_id
            }
        )
        
        return {
            "access_token": access_token,
            "admin_id": user.user_id,
            "username": user.username,
            "role": role_names[0] if role_names else "Admin"
        }

    async def get_current_admin(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = await self.repository.get_user_by_id(user_id)
        if not user or not user.is_active:
            return None
        
        roles = await self.repository.get_user_roles(user_id)
        role_names = [r.name for r in roles]
        
        result = {
            "user_id": user.user_id,
            "username": user.username,
            "roles": role_names,
            "institute_id": user.institute_id,
            "is_active": user.is_active
        }
        
        if user.institute_id:
            institute = await self.repository.get_institute_by_id(user.institute_id)
            if institute:
                result["institute_name"] = institute.name
                result["institute_code"] = institute.code
        
        if user.employee_id:
            result["is_institute_admin"] = True
        
        return result

    async def change_password(self, user_id: int, password_data: ChangePasswordRequest) -> Dict[str, Any]:
        user = await self.repository.get_user_by_id(user_id)
        if not user or not self.verify_password(password_data.old_password, user.password_hash):
            return {"error": "Invalid old password"}
        
        new_hash = self.hash_password(password_data.new_password)
        success = await self.repository.update_password(user_id, new_hash)
        
        if success:
            return {"message": "Password changed successfully"}
        return {"error": "Failed to change password"}

    async def get_all_institute_admins(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        admins = await self.repository.get_all_institute_admins(skip, limit)
        result = []
        for admin in admins:
            institute = await self.repository.get_institute_by_id(admin.institute_id) if admin.institute_id else None
            result.append({
                "admin_id": admin.user_id,
                "username": admin.username,
                "institute_id": admin.institute_id,
                "institute_name": institute.name if institute else None,
                "is_active": admin.is_active,
                "created_at": admin.created_at
            })
        return result

    async def update_admin_status(self, user_id: int, status_data: AdminStatusUpdate) -> Optional[Dict[str, Any]]:
        is_active = status_data.status == AdminStatusEnum.active
        user = await self.repository.update_user_status(user_id, is_active)
        if user:
            return {
                "admin_id": user.user_id,
                "status": status_data.status,
                "message": f"Admin status updated to {status_data.status}"
            }
        return None

    async def get_institute_admin_by_institute(self, institute_id: int) -> Optional[Dict[str, Any]]:
        admin = await self.repository.get_institute_admin(institute_id)
        if not admin:
            return None
        
        institute = await self.repository.get_institute_by_id(institute_id)
        
        return {
            "admin_id": admin.user_id,
            "username": admin.username,
            "institute_id": admin.institute_id,
            "institute_name": institute.name if institute else None,
            "is_active": admin.is_active,
            "created_at": admin.created_at
        }