from app.di.attendance import provide_checkin, provide_checkout, provide_heatmap
from app.di.auth import provide_login
from app.di.leave_balances import provide_get_my_leave_balance, provide_get_user_leave_balance, provide_update_leave_balance
from app.di.leaves import (
    provide_cancel_leave,
    provide_create_leave,
    provide_list_leave,
    provide_review_leave,
    provide_update_leave,
)
from app.di.notifications import provide_list_notifications
from app.di.tasks import (
    provide_assign_task,
    provide_complete_task,
    provide_create_task,
    provide_list_tasks,
)
from app.di.users import provide_create_user, provide_list_users

__all__ = [
    "provide_assign_task",
    "provide_checkin",
    "provide_checkout",
    "provide_complete_task",
    "provide_create_leave",
    "provide_create_task",
    "provide_create_user",
    "provide_cancel_leave",
    "provide_get_my_leave_balance",
    "provide_get_user_leave_balance",
    "provide_heatmap",
    "provide_list_leave",
    "provide_list_notifications",
    "provide_list_tasks",
    "provide_list_users",
    "provide_login",
    "provide_update_leave_balance",
    "provide_update_leave",
    "provide_review_leave",
]
