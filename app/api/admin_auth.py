
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database.database import db_manager
from app.features.admin_auth.schemas import (
    SuperAdminCreate, InstituteAdminCreate, AdminLoginRequest,
    AdminLoginResponse, InstituteAdminResponse, ChangePasswordRequest,
    AdminStatusUpdate
)
from app.features.admin_auth.services import AdminAuthService
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter(prefix="/api/auth", tags=["Admin Authentication"])

async def get_current_admin(authorization: str = Header(...), db: AsyncSession = Depends(db_manager.get_session)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    service = AdminAuthService(db)
    admin = await service.get_current_admin(user_id)
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found or inactive")
    
    return admin

async def require_super_admin(current_admin: dict = Depends(get_current_admin)):
    if "Super Admin" not in current_admin.get("roles", []):
        raise HTTPException(status_code=403, detail="Super admin access required")
    return current_admin

async def require_institute_admin(current_admin: dict = Depends(get_current_admin)):
    roles = current_admin.get("roles", [])
    if "Super Admin" not in roles and "Institute Admin" not in roles:
        raise HTTPException(status_code=403, detail="Institute admin access required")
    return current_admin

@router.post("/super-admin/create", response_model=dict)
async def create_super_admin(admin_data: SuperAdminCreate, db: AsyncSession = Depends(db_manager.get_session)):
    service = AdminAuthService(db)
    result = await service.create_super_admin(admin_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/institute-admin/create", response_model=dict)
async def create_institute_admin(
    admin_data: InstituteAdminCreate,
    current_admin: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = AdminAuthService(db)
    result = await service.create_institute_admin(admin_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(login_data: AdminLoginRequest, db: AsyncSession = Depends(db_manager.get_session)):
    service = AdminAuthService(db)
    result = await service.login(login_data)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result

@router.get("/me", response_model=dict)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    return current_admin

@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: ChangePasswordRequest,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = AdminAuthService(db)
    result = await service.change_password(current_admin["user_id"], password_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/institute-admins", response_model=List[dict])
async def get_all_institute_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = AdminAuthService(db)
    return await service.get_all_institute_admins(skip, limit)

@router.patch("/institute-admins/{admin_id}/status", response_model=dict)
async def update_admin_status(
    admin_id: int,
    status_data: AdminStatusUpdate,
    current_admin: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = AdminAuthService(db)
    result = await service.update_admin_status(admin_id, status_data)
    if not result:
        raise HTTPException(status_code=404, detail="Admin not found")
    return result

@router.get("/institute/{institute_id}/admin", response_model=dict)
async def get_institute_admin(
    institute_id: int,
    current_admin: dict = Depends(require_institute_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = AdminAuthService(db)
    result = await service.get_institute_admin_by_institute(institute_id)
    if not result:
        raise HTTPException(status_code=404, detail="Institute admin not found")
    return result