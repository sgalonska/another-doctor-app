from fastapi import APIRouter

from app.api.api_v1.endpoints import cases, doctors, matching, upload, tasks, research, monitoring

api_router = APIRouter()
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])