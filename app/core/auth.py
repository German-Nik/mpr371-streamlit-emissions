import hashlib
import hmac
from typing import Optional, Dict, Any
from .db import get_conn

def hash_password(password: str) -> str:
    # Simple SHA-256 for prototype. For production: bcrypt/argon2 with per-user salt.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    candidate = hash_password(password)
    return hmac.compare_digest(candidate, password_hash)

def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT username, role, branch_id, password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    if not verify_password(password, row["password_hash"]):
        return None
    return {"username": row["username"], "role": row["role"], "branch_id": row["branch_id"]}

def get_branch_name(branch_id: Optional[int]) -> Optional[str]:
    if branch_id is None:
        return None
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT branch_name FROM branches WHERE branch_id = ?", (branch_id,))
    row = cur.fetchone()
    conn.close()
    return row["branch_name"] if row else None
