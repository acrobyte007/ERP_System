# feature/institute/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update, delete
from sqlalchemy.orm import selectinload
from app.database.models import (
    Institute, AcademicYear, Student, Employee, Standard,
    Subject, Hostel, User, StudentEnrollment
)
from typing import Optional, List, Dict, Any
from app.features.institute.schemas import InstituteStatusEnum

class InstituteRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_institute(self, institute_data: Dict[str, Any]) -> Institute:
        institute = Institute(**institute_data)
        self.db.add(institute)
        await self.db.commit()
        await self.db.refresh(institute)
        return institute

    async def get_institute(self, institute_id: int) -> Optional[Institute]:
        result = await self.db.execute(
            select(Institute).where(
                Institute.institute_id == institute_id,
                Institute.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_all_institutes(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Institute]:
        query = select(Institute).where(Institute.is_active == True)
        if status:
            query = query.where(Institute.status == status)
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_institute(self, institute_id: int, update_data: Dict[str, Any]) -> Optional[Institute]:
        institute = await self.get_institute(institute_id)
        if institute:
            for key, value in update_data.items():
                setattr(institute, key, value)
            await self.db.commit()
            await self.db.refresh(institute)
        return institute

    async def delete_institute(self, institute_id: int) -> bool:
        institute = await self.get_institute(institute_id)
        if institute:
            institute.is_active = False
            institute.status = InstituteStatusEnum.archived
            await self.db.commit()
            return True
        return False

    async def update_status(self, institute_id: int, status: str) -> Optional[Institute]:
        institute = await self.get_institute(institute_id)
        if institute:
            institute.status = status
            if status == InstituteStatusEnum.archived:
                institute.is_active = False
            elif status == InstituteStatusEnum.active:
                institute.is_active = True
            await self.db.commit()
            await self.db.refresh(institute)
        return institute

    async def get_dashboard_stats(self, institute_id: int) -> Dict[str, Any]:
        total_students_result = await self.db.execute(
            select(func.count(Student.student_id)).where(
                Student.institute_id == institute_id,
                Student.is_active == True
            )
        )
        total_students = total_students_result.scalar() or 0

        total_employees_result = await self.db.execute(
            select(func.count(Employee.employee_id)).where(
                Employee.institute_id == institute_id,
                Employee.is_active == True
            )
        )
        total_employees = total_employees_result.scalar() or 0

        total_academic_years_result = await self.db.execute(
            select(func.count(AcademicYear.academic_year_id)).where(
                AcademicYear.institute_id == institute_id
            )
        )
        total_academic_years = total_academic_years_result.scalar() or 0

        total_standards_result = await self.db.execute(
            select(func.count(Standard.standard_id)).where(
                Standard.institute_id == institute_id,
                Standard.is_active == True
            )
        )
        total_standards = total_standards_result.scalar() or 0

        total_subjects_result = await self.db.execute(
            select(func.count(Subject.subject_id)).where(
                Subject.institute_id == institute_id,
                Subject.is_active == True
            )
        )
        total_subjects = total_subjects_result.scalar() or 0

        total_hostels_result = await self.db.execute(
            select(func.count(Hostel.hostel_id)).where(
                Hostel.institute_id == institute_id,
                Hostel.is_active == True
            )
        )
        total_hostels = total_hostels_result.scalar() or 0

        total_users_result = await self.db.execute(
            select(func.count(User.user_id)).where(
                User.institute_id == institute_id,
                User.is_active == True
            )
        )
        total_users = total_users_result.scalar() or 0

        active_enrollments_result = await self.db.execute(
            select(func.count(StudentEnrollment.enrollment_id)).where(
                StudentEnrollment.institute_id == institute_id,
                StudentEnrollment.status == "active"
            )
        )
        active_enrollments = active_enrollments_result.scalar() or 0

        current_academic_year_result = await self.db.execute(
            select(AcademicYear.name).where(
                AcademicYear.institute_id == institute_id,
                AcademicYear.is_current == True
            )
        )
        current_academic_year = current_academic_year_result.scalar_one_or_none()

        return {
            "total_students": total_students,
            "total_employees": total_employees,
            "total_academic_years": total_academic_years,
            "total_standards": total_standards,
            "total_subjects": total_subjects,
            "total_hostels": total_hostels,
            "total_users": total_users,
            "active_enrollments": active_enrollments,
            "current_academic_year": current_academic_year
        }