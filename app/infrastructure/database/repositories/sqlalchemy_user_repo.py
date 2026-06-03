"""SQLAlchemy 2.0 async implementation của UserRepository.

Điểm cốt lõi của Passport Pattern:
    ``find_by_id`` và ``find_by_email`` nạp sớm (eager-load) chain:
    UserModel → RoleModel → List[PermissionModel]

    Nhờ vào ``lazy="selectin"`` trên ``UserModel.role`` và
    ``RoleModel.permissions``, SQLAlchemy phát tối đa 2 câu SELECT IN
    thay vì N+1 query.  Kết quả được map sang Domain Entity ``User``
    với tập ``permissions: set[str]`` đã sẵn sàng cho RBACService.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.models.user_model import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """Concrete async repository — SQLAlchemy 2.0 + asyncpg."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _to_entity(self, model: UserModel) -> User:
        """Map ORM UserModel → Domain User với permissions đã eager-load.

        ``model.role.permissions`` đã được SQLAlchemy nạp sẵn nhờ chain
        selectinload → không có lazy-load bổ sung tại đây.
        """
        permissions: set[str] = (
            {p.code for p in model.role.permissions}
            if model.role and model.role.permissions
            else set()
        )
        return User(
            id=model.id,
            employee_code=model.employee_code,
            email=model.email,
            full_name=model.full_name,
            role_name=model.role.name if model.role else "",
            role_id=model.role_id,
            permissions=permissions,
            phone=model.phone,
            job_title=model.job_title,
            contact_type=model.contact_type,
            department_id=model.department_id,
            manager_id=model.manager_id,
            hire_date=model.hire_date,
            is_active=model.is_active,
            hashed_password=model.hashed_password,
        )

    def _base_stmt(self):
        """Câu lệnh SELECT cơ sở với eager-load chain đầy đủ.

        selectinload(UserModel.role).selectinload(RoleModel.permissions)
        phát 2 câu SELECT IN:
            1. SELECT * FROM roles WHERE id IN (...)
            2. SELECT p.* FROM permissions p
               JOIN role_permissions rp ON rp.permission_id = p.id
               WHERE rp.role_id IN (...)

        Tổng: 1 (user) + 2 (role + permissions) = 3 câu mỗi request,
        thay vì N+1 với lazy load.
        """
        from app.infrastructure.database.models.role_model import RoleModel
        from app.infrastructure.database.models.permission_model import PermissionModel  # noqa

        return select(UserModel).options(
            selectinload(UserModel.role).selectinload(RoleModel.permissions)
        )

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def find_by_id(self, user_id: int) -> User | None:
        stmt = self._base_stmt().where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_by_email(self, email: str) -> User | None:
        stmt = self._base_stmt().where(UserModel.email == email)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_all(self) -> list[User]:
        stmt = self._base_stmt().order_by(UserModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_department(self, department_id: int) -> list[User]:
        stmt = (
            self._base_stmt()
            .where(UserModel.department_id == department_id)
            .order_by(UserModel.id)
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def create(self, user: User, *, hashed_password: str) -> User:
        """Tạo user mới. ``hashed_password`` truyền riêng để tách biệt concern."""
        model = UserModel(
            employee_code=user.employee_code,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            phone=user.phone,
            job_title=user.job_title,
            contact_type=user.contact_type,
            department_id=user.department_id,
            manager_id=user.manager_id,
            hire_date=user.hire_date,
            is_active=user.is_active,
            role_id=user.role_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return await self.find_by_id(model.id)  # type: ignore[return-value]

    async def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"User {user.id} not found")
        model.full_name = user.full_name
        model.phone = user.phone
        model.job_title = user.job_title
        model.contact_type = user.contact_type
        model.department_id = user.department_id
        model.manager_id = user.manager_id
        model.is_active = user.is_active
        await self._session.flush()
        return await self.find_by_id(model.id)  # type: ignore[return-value]

    async def delete(self, user_id: int) -> None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
