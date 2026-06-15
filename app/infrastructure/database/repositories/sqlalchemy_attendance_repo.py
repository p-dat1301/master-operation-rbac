"""SQLAlchemy 2.0 async implementation của AttendanceRepository."""
from __future__ import annotations

from datetime import date, datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.attendance import Attendance
from app.domain.repositories.attendance_repository import AttendanceRepository
from app.infrastructure.database.models.attendance_model import AttendanceModel


class SQLAlchemyAttendanceRepository(AttendanceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def _to_entity(self, model: AttendanceModel) -> Attendance:
        return Attendance(
            id=model.id,
            user_id=model.user_id,
            date=model.date,
            check_in=self._as_utc(model.check_in),
            check_out=self._as_utc(model.check_out),
            total_minutes=model.total_minutes,
            ip_address=model.ip_address,
            department_id=model.department_id,
            status=model.status,
            note=model.note,
        )

    async def find_by_id(self, attendance_id: int) -> Attendance | None:
        stmt = select(AttendanceModel).where(AttendanceModel.id == attendance_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def find_by_user_date(self, user_id: int, day: date) -> Attendance | None:
        stmt = select(AttendanceModel).where(
            AttendanceModel.user_id == user_id,
            AttendanceModel.date == day,
        )
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        return self._to_entity(model) if model else None

    async def list_by_user(self, user_id: int) -> list[Attendance]:
        stmt = select(AttendanceModel).where(AttendanceModel.user_id == user_id).order_by(AttendanceModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_departments(self, department_ids: set[int]) -> list[Attendance]:
        stmt = select(AttendanceModel).where(AttendanceModel.department_id.in_(department_ids)).order_by(AttendanceModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_by_date_range(self, start_date: date, end_date: date) -> list[Attendance]:
        stmt = select(AttendanceModel).where(
            AttendanceModel.date >= start_date,
            AttendanceModel.date <= end_date,
        ).order_by(AttendanceModel.id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def create(self, attendance: Attendance) -> Attendance:
        model = AttendanceModel(
            user_id=attendance.user_id,
            date=attendance.date,
            check_in=self._as_utc(attendance.check_in),
            check_out=self._as_utc(attendance.check_out),
            total_minutes=attendance.total_minutes,
            ip_address=attendance.ip_address,
            department_id=attendance.department_id,
            status=attendance.status,
            note=attendance.note,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update(self, attendance: Attendance) -> Attendance:
        stmt = select(AttendanceModel).where(AttendanceModel.id == attendance.id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Attendance {attendance.id} not found")
        model.check_in = self._as_utc(attendance.check_in)
        model.check_out = self._as_utc(attendance.check_out)
        model.total_minutes = attendance.total_minutes
        model.ip_address = attendance.ip_address
        model.status = attendance.status
        model.note = attendance.note
        model.department_id = attendance.department_id
        await self._session.flush()
        return self._to_entity(model)

    async def checkout(
        self,
        attendance_id: int,
        check_out: datetime,
        total_minutes: int | None,
    ) -> Attendance:
        stmt = select(AttendanceModel).where(AttendanceModel.id == attendance_id)
        result = await self._session.execute(stmt)
        model = result.scalars().first()
        if not model:
            raise ValueError(f"Attendance {attendance_id} not found")
        model.check_out = self._as_utc(check_out)
        model.total_minutes = total_minutes
        model.status = "checked_out"
        await self._session.flush()
        return self._to_entity(model)
