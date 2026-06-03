from fastapi import APIRouter, Depends

from app.presentation.dependencies.auth_deps import get_current_user

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/")
async def list_notifications(actor=Depends(get_current_user)):
    # Placeholder: returns empty list
    return []
