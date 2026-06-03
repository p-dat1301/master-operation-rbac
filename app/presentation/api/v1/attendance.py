from fastapi import APIRouter, Depends

from app.presentation.schemas.attendance_schema import CheckinRequest, AttendanceResponse, HeatmapRequest
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.container import get_checkin_use_case
from app.application.dtos.attendance import CheckinInput

router = APIRouter(prefix="/api/v1/attendance", tags=["attendance"])


@router.post("/checkin", response_model=AttendanceResponse)
async def checkin(data: CheckinRequest, db=Depends(get_db)):
    use_case = get_checkin_use_case(db)
    dto = CheckinInput(**data.dict())
    created = await use_case.execute(dto)
    return AttendanceResponse.from_entity(created)


@router.get("/heatmap")
async def heatmap(filter: HeatmapRequest = Depends(), actor=Depends(get_current_user), db=Depends(get_db)):
    # Placeholder: application has heatmap use case; implement when ready
    return {"status": "not_implemented"}
