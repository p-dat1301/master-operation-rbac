from dataclasses import dataclass
from typing import Optional

@dataclass
class Department:
    id: int
    name: str
    level: int
    parent_id: Optional[int] = None
    head_id: Optional[int] = None
    code: str = ""
    