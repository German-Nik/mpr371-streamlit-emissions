from dataclasses import dataclass
from typing import Optional

@dataclass
class UserSession:
    username: str
    role: str  # 'admin' or 'user'
    branch_id: Optional[int] = None
