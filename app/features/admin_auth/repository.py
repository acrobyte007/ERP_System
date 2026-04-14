# feature/admin_auth/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.database.models import User, Role, UserRole, Employee, Institute
from typing import Optional, List, Dict, Any

class AdminAuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: Dict[str, Any]) -> User:
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_employee(self, employee_data: Dict[str, Any]) -> Employee:
        employee = Employee(**employee_data)
        self.db.add(employee)
        await self.db.commit()
        await self.db.refresh(employee)
        return employee

    async def get_role_by_name(self, role_name: str, institute_id: Optional[int] = None) -> Optional[Role]:
        query = select(Role).where(Role.name == role_name)
        if institute_id:
            query = query.where(Role.institute_id == institute_id)
        else:
            query = query.where(Role.institute_id.is_(None))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_role(self, role_data: Dict[str, Any]) -> Role:
        role = Role(**role_data)
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def assign_role_to_user(self, user_id: int, role_id: int) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.commit()
        await self.db.refresh(user_role)
        return user_role

    async def get_user_roles(self, user_id: int) -> List[Role]:
        result = await self.db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.role_id)
            .where(UserRole.user_id == user_id)
        )
        return result.scalars().all()

    async def get_institute_admin(self, institute_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .join(UserRole, UserRole.user_id == User.user_id)
            .join(Role, Role.role_id == UserRole.role_id)
            .where(
                User.institute_id == institute_id,
                Role.name == "Institute Admin",
                User.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_all_institute_admins(self, skip: int = 0, limit: int = 100) -> List[User]:
        result = await self.db.execute(
            select(User)
            .join(UserRole, UserRole.user_id == User.user_id)
            .join(Role, Role.role_id == UserRole.role_id)
            .where(Role.name == "Institute Admin")
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update_user_status(self, user_id: int, is_active: bool) -> Optional[User]:
        user = await self.get_user_by_id(user_id)
        if user:
            user.is_active = is_active
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def update_password(self, user_id: int, password_hash: str) -> bool:
        user = await self.get_user_by_id(user_id)
        if user:
            user.password_hash = password_hash
            await self.db.commit()
            return True
        return False

    async def get_institute_by_id(self, institute_id: int) -> Optional[Institute]:
        result = await self.db.execute(
            select(Institute).where(Institute.institute_id == institute_id)
        )
        return result.scalar_one_or_none()