from fastapi import APIRouter, Depends, Path

from app.presentation.schemas.notification_schema import NotificationResponse
from app.presentation.dependencies.db_deps import get_db
from app.presentation.dependencies.auth_deps import get_current_user
from app.di.notifications import provide_list_notifications
from app.infrastructure.database.repositories.sqlalchemy_notification_repo import SQLAlchemyNotificationRepository

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationResponse])
async def list_notifications(actor=Depends(get_current_user), db=Depends(get_db)):
    use_case = provide_list_notifications(db)
    dtos = await use_case.execute(actor)
    return [NotificationResponse.from_dto(d) for d in dtos]


@router.put("/{id}/read", response_model=NotificationResponse)
async def mark_notification_read(id: int = Path(...), actor=Depends(get_current_user), db=Depends(get_db)):
    repo = SQLAlchemyNotificationRepository(db)
    notification = await repo.find_by_id(id)
    if notification is None:
        from app.domain.exceptions import ResourceNotFound
        raise ResourceNotFound("Notification not found")
    if notification.recipient_id != actor.id:
        from app.domain.exceptions import PermissionDenied
        raise PermissionDenied("Cannot mark another user's notification as read")
    updated = await repo.mark_as_read(id)
    from app.application.dtos.notification import NotificationOutput
    return NotificationResponse.from_dto(NotificationOutput.from_entity(updated))


@router.put("/read-all")
async def mark_all_notifications_read(actor=Depends(get_current_user), db=Depends(get_db)):
    repo = SQLAlchemyNotificationRepository(db)
    count = await repo.mark_all_as_read(actor.id)
    return {"marked_count": count}
