from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class User:
    """Rich Domain Entity cho người dùng.

    Trường ``permissions`` là một ``set[str]`` chứa mã quyền phẳng (ví dụ:
    ``{"task:create", "leave:approve"}``).  Tập hợp này được nạp sớm
    (Eager-Load) từ DB tại tầng Repository mỗi khi xác thực Request, và được
    tầng Domain sử dụng để kiểm tra quyền thuần túy (O(1) — không I/O).

    Không bao giờ inject ``AsyncSession`` hay bất kỳ ORM object nào vào đây.
    """

    id: int
    employee_code: str
    email: str
    full_name: str
    role_name: str                              # tên vai trò: "admin", "manager", …
    permissions: set[str] = field(default_factory=set)  # quyền từ DB, nạp sớm
    phone: Optional[str] = None
    job_title: Optional[str] = None
    contact_type: Optional[str] = None
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    hire_date: Optional[date] = None
    is_active: bool = True