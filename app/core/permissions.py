from functools import wraps
from typing import Callable

from fastapi import Request, HTTPException


ROLES = {
    "admin": 100,
    "incident_leader": 70,
    "breathing_supervisor": 50,
    "recorder": 30,
    "readonly": 10,
}


def require_role(*roles: str) -> Callable:
    """FastAPI dependency that enforces role membership."""
    def dependency(request: Request):
        user = getattr(request.state, "user", None)
        if user is None:
            raise HTTPException(status_code=401, detail="Nicht angemeldet")
        user_roles = {r.code for r in user.roles}
        if not user_roles.intersection(set(roles) | {"admin"}):
            raise HTTPException(status_code=403, detail="Keine Berechtigung")
        return user
    return dependency


def has_role(user, *roles: str) -> bool:
    if user is None:
        return False
    user_roles = {r.code for r in user.roles}
    return bool(user_roles.intersection(set(roles) | {"admin"}))
