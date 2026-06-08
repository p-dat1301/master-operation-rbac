from fastapi import APIRouter, Depends

from app.presentation.schemas.attendance_schema import CheckinRequest, AttendanceResponse, HeatmapRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di import provide_checkin, provide_checkout, provide_heatmap

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])


@router.post("/checkin", response_model=AttendanceResponse)
async def checkin(data: CheckinRequest, actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_checkin(db)
    dto = data.to_dto()
    result = await use_case.execute(actor, dto)
    return AttendanceResponse.from_dto(result)


@router.get("/heatmap", response_model=list[AttendanceResponse])
async def heatmap(filter: HeatmapRequest = Depends(), actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_heatmap(db)
    records = await use_case.execute(actor, filter.to_dto())
    return [AttendanceResponse.from_dto(r) for r in records]


@router.post("/checkout", response_model=AttendanceResponse)
async def checkout(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_checkout(db)
    result = await use_case.execute(actor)
    return AttendanceResponse.from_dto(result)
