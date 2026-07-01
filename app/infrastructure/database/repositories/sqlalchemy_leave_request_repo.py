"""SQLAlchemy 2.0 async implementation của LeaveRequestRepository."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.leave_request import LeaveRequest, LeaveRequestStatus
from app.domain.repositories.leave_request_repository import LeaveRequestRepository
from app.infrastructure.database.models.leave_request_model import LeaveRequestModel


class SQLAlchemyLeaveRequestRepository(LeaveRequestRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _to_entity(self, model: LeaveRequestModel) -> LeaveRequest:
        return LeaveRequest(
            id=model.id,
            requester_id=model.requester_id,
            leave_type=model.leave_type,
            start_date=model.start_date,
            end_date=model.end_date,
            reason=model.reason,
            status=LeaveRequestStatus(model.status),
            department_id=model.department_id,
            reviewed_by=model.reviewer_id,
            reviewed_at=self._as_utc(model.reviewed_at),
            created_at=self._as_utc(model.created_at),
        )

    async def find_by_id(self, leave_id: int) -> LeaveRequest | None:
        stmt = select(LeaveRequestModel).where(LeaveRequestModel.id == leave_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[LeaveRequest]:
        stmt = select(LeaveRequestModel).order_by(LeaveRequestModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_requester(self, requester_id: int) -> list[LeaveRequest]:
        stmt = select(LeaveRequestModel).where(LeaveRequestModel.requester_id == requester_id).order_by(LeaveRequestModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_reviewer(self, reviewer_id: int) -> list[LeaveRequest]:
        stmt = select(LeaveRequestModel).where(LeaveRequestModel.reviewer_id == reviewer_id).order_by(LeaveRequestModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_status(self, status: str) -> list[LeaveRequest]:
        stmt = select(LeaveRequestModel).where(LeaveRequestModel.status == status).order_by(LeaveRequestModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_departments(self, department_ids: set[int]) -> list[LeaveRequest]:
        stmt = select(LeaveRequestModel).where(LeaveRequestModel.department_id.in_(department_ids)).order_by(LeaveRequestModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, leave: LeaveRequest) -> LeaveRequest:
        model = LeaveRequestModel(
            requester_id=leave.requester_id,
            leave_type=leave.leave_type,
            start_date=leave.start_date,
            end_date=leave.end_date,
            reason=leave.reason,
            status=leave.status.value,
            department_id=leave.department_id,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, leave: LeaveRequest) -> LeaveRequest:
        stmt = select(LeaveRequestModel).where(LeaveRequestModel.id == leave.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"LeaveRequest {leave.id} not found")
        model.leave_type = leave.leave_type
        model.start_date = leave.start_date
        model.end_date = leave.end_date
        model.reason = leave.reason
        model.status = leave.status.value
        model.department_id = leave.department_id
        await self._session.flush()
        return self._to_entity(model)

    async def update_status(
        self,
        leave_id: int,
        status: str,
        reviewed_by: int | None,
        rejection_reason: str | None = None,
    ) -> LeaveRequest:
        stmt = select(LeaveRequestModel).where(LeaveRequestModel.id == leave_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"LeaveRequest {leave_id} not found")
        model.status = status
        model.reviewer_id = reviewed_by
        model.reviewed_at = datetime.now(timezone.utc)
        await self._session.flush()
        return self._to_entity(model)
