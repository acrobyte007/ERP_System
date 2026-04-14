# api/institute.py (updated with admin auth)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database.database import db_manager
from app.features.institute.schemas import (
    InstituteCreate, InstituteUpdate, InstituteStatusUpdate
)
from app.features.institute.services import InstituteService
from app.api.admin_auth import require_institute_admin,require_super_admin

router = APIRouter(prefix="/api/institutes", tags=["Institute Management"])

@router.get("/")
async def list_institutes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    current_admin: dict = Depends(require_institute_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = InstituteService(db)
    if "Super Admin" in current_admin.get("roles", []):
        return await service.get_all_institutes(skip, limit, status)
    else:
        institute_id = current_admin.get("institute_id")
        institute = await service.get_institute(institute_id)
        return [institute] if institute else []

@router.get("/{institute_id}")
async def get_institute_details(
    institute_id: int,
    current_admin: dict = Depends(require_institute_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    if "Super Admin" not in current_admin.get("roles", []) and current_admin.get("institute_id") != institute_id:
        raise HTTPException(status_code=403, detail="Access denied to this institute")
    
    service = InstituteService(db)
    institute = await service.get_institute(institute_id)
    if not institute:
        raise HTTPException(status_code=404, detail="Institute not found")
    return institute

@router.post("/")
async def create_institute(
    institute_data: InstituteCreate,
    current_admin: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = InstituteService(db)
    result = await service.create_institute(institute_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.put("/{institute_id}")
async def update_institute(
    institute_id: int,
    update_data: InstituteUpdate,
    current_admin: dict = Depends(require_institute_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    if "Super Admin" not in current_admin.get("roles", []) and current_admin.get("institute_id") != institute_id:
        raise HTTPException(status_code=403, detail="Access denied to this institute")
    
    service = InstituteService(db)
    result = await service.update_institute(institute_id, update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Institute not found")
    return result

@router.delete("/{institute_id}")
async def delete_institute(
    institute_id: int,
    current_admin: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = InstituteService(db)
    result = await service.delete_institute(institute_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/{institute_id}/stats")
async def get_institute_stats(
    institute_id: int,
    current_admin: dict = Depends(require_institute_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    if "Super Admin" not in current_admin.get("roles", []) and current_admin.get("institute_id") != institute_id:
        raise HTTPException(status_code=403, detail="Access denied to this institute")
    
    service = InstituteService(db)
    stats = await service.get_dashboard_stats(institute_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Institute not found")
    return stats

@router.patch("/{institute_id}/status")
async def update_institute_status(
    institute_id: int,
    status_data: InstituteStatusUpdate,
    current_admin: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(db_manager.get_session)
):
    service = InstituteService(db)
    result = await service.update_status(institute_id, status_data)
    if not result:
        raise HTTPException(status_code=404, detail="Institute not found")
    return result