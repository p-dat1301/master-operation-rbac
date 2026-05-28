from dataclasses import dataclass

@dataclass
class RolePermission:
    role_id: int
    permission_id: int