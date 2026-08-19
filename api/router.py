from fastapi import APIRouter
from .routes import (
    admin,
    audit,
    auth,
    devices,
    organizations,
    pin,
    sessions,
    users,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(sessions.router)
api_router.include_router(devices.router)
api_router.include_router(pin.router)
api_router.include_router(organizations.router)
api_router.include_router(audit.router)
api_router.include_router(admin.router)

__all__ = ["api_router"]