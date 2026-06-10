"""SQLAlchemy 2.0 async implementation của LeaveBalanceRepository."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.leave_balance import LeaveBalance
from app.domain.repositories.leave_balance_repository import LeaveBalanceRepository
from app.infrastructure.database.models.leave_balance_model import LeaveBalanceModel


class SQLAlchemyLeaveBalanceRepository(LeaveBalanceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: LeaveBalanceModel) -> LeaveBalance:
        remaining = model.total_days - model.used_days
        return LeaveBalance(
            id=model.id,
            user_id=model.user_id,
            year=model.year,
            total_days=float(model.total_days),
            used_days=float(model.used_days),
            pending_days=0.0,
            remaining_days=remaining,
            updated_at=model.updated_at,
        )

    async def find_by_id(self, balance_id: int) -> LeaveBalance | None:
        stmt = select(LeaveBalanceModel).where(LeaveBalanceModel.id == balance_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_by_user_year(self, user_id: int, year: int) -> LeaveBalance | None:
        stmt = select(LeaveBalanceModel).where(
            LeaveBalanceModel.user_id == user_id,
            LeaveBalanceModel.year == year,
        )
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_by_user(self, user_id: int) -> list[LeaveBalance]:
        stmt = select(LeaveBalanceModel).where(LeaveBalanceModel.user_id == user_id).order_by(LeaveBalanceModel.year)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, balance: LeaveBalance) -> LeaveBalance:
        model = LeaveBalanceModel(
            user_id=balance.user_id,
            year=balance.year,
            total_days=int(balance.total_days),
            used_days=int(balance.used_days),
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, balance: LeaveBalance) -> LeaveBalance:
        stmt = select(LeaveBalanceModel).where(LeaveBalanceModel.id == balance.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"LeaveBalance {balance.id} not found")
        model.total_days = int(balance.total_days)
        model.used_days = int(balance.used_days)
        await self._session.flush()
        return self._to_entity(model)

    async def upsert(self, balance: LeaveBalance) -> LeaveBalance:
        existing = await self.find_by_user_year(balance.user_id, balance.year)
        if existing:
            balance_with_id = LeaveBalance(
                id=existing.id,
                user_id=balance.user_id,
                year=balance.year,
                total_days=balance.total_days,
                used_days=balance.used_days,
                pending_days=balance.pending_days,
                remaining_days=balance.remaining_days,
                updated_at=balance.updated_at,
            )
            return await self.update(balance_with_id)
        return await self.create(balance)

    async def delete(self, balance_id: int) -> None:
        stmt = select(LeaveBalanceModel).where(LeaveBalanceModel.id == balance_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if model:
            await self._session.delete(model)
            await self._session.flush()
