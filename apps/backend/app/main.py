from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.middleware.monitoring import MonitoringMiddleware

app = FastAPI(
    title="Another Doctor API",
    description="Medical specialist matching service API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(MonitoringMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Initialize task handlers for local development
if settings.ENVIRONMENT == "development":
    try:
        from app.services.task_handlers import initialize_task_handlers
        initialize_task_handlers()
    except Exception as e:
        print(f"Warning: Failed to initialize task handlers: {e}")

@app.get("/")
def root():
    return {"message": "Another Doctor API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}