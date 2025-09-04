"""
Monitoring middleware for FastAPI requests
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.dependencies import get_monitoring_service


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics"""
    
    def __init__(self, app):
        super().__init__(app)
        self.monitoring = get_monitoring_service()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response: Response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Track the request
        self.monitoring.track_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        
        return response