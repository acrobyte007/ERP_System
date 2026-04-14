# feature/institute/services.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.institute.repository import InstituteRepository
from app.features.institute.schemas import (
    InstituteCreate, InstituteUpdate, InstituteStatusUpdate
)
from typing import Optional, List, Dict, Any

class InstituteService:
    def __init__(self, db: AsyncSession):
        self.repository = InstituteRepository(db)

    async def create_institute(self, institute_data: InstituteCreate) -> Dict[str, Any]:
        institutes = await self.repository.get_all_institutes(status=None)
        for inst in institutes:
            if inst.code == institute_data.code:
                return {"error": f"Institute with code {institute_data.code} already exists"}
        institute = await self.repository.create_institute(institute_data.dict())
        return {
            "institute_id": institute.institute_id,
            "message": "Institute created successfully"
        }

    async def get_institute(self, institute_id: int) -> Optional[Dict[str, Any]]:
        institute = await self.repository.get_institute(institute_id)
        if institute:
            return {
                "institute_id": institute.institute_id,
                "name": institute.name,
                "code": institute.code,
                "email": institute.email,
                "phone": institute.phone,
                "address": institute.address,
                "academic_structure": institute.academic_structure,
                "academic_mode": institute.academic_mode,
                "status": institute.status,
                "is_active": institute.is_active,
                "created_at": institute.created_at,
                "updated_at": institute.updated_at
            }
        return None

    async def get_all_institutes(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        institutes = await self.repository.get_all_institutes(skip, limit, status)
        return [
            {
                "institute_id": i.institute_id,
                "name": i.name,
                "code": i.code,
                "status": i.status,
                "is_active": i.is_active,
                "created_at": i.created_at
            }
            for i in institutes
        ]

    async def update_institute(self, institute_id: int, update_data: InstituteUpdate) -> Optional[Dict[str, Any]]:
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if not update_dict:
            return None
        institute = await self.repository.update_institute(institute_id, update_dict)
        if institute:
            return {
                "institute_id": institute.institute_id,
                "message": "Institute updated successfully"
            }
        return None

    async def delete_institute(self, institute_id: int) -> Dict[str, Any]:
        success = await self.repository.delete_institute(institute_id)
        if success:
            return {"message": "Institute deleted successfully"}
        return {"error": "Institute not found"}

    async def update_status(self, institute_id: int, status_data: InstituteStatusUpdate) -> Optional[Dict[str, Any]]:
        institute = await self.repository.update_status(institute_id, status_data.status)
        if institute:
            return {
                "institute_id": institute.institute_id,
                "status": institute.status,
                "message": f"Institute status updated to {institute.status}"
            }
        return None

    async def get_dashboard_stats(self, institute_id: int) -> Optional[Dict[str, Any]]:
        institute = await self.repository.get_institute(institute_id)
        if not institute:
            return None
        return await self.repository.get_dashboard_stats(institute_id)