from fastapi import APIRouter

from app.api.api_v1.endpoints import cases, doctors, matching, upload

api_router = APIRouter()
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])