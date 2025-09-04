"""
Monitoring endpoints for health checks and metrics
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.dependencies import get_monitoring_service

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}


@router.get("/metrics")
def get_metrics(monitoring_service = Depends(get_monitoring_service)) -> Dict[str, Any]:
    """
    Basic metrics endpoint - in local development this just returns status
    In GCP this would return formatted metrics or redirect to Cloud Monitoring
    """
    if monitoring_service.is_local:
        return {
            "status": "metrics_logged_to_console",
            "note": "In development mode, metrics are logged to console. In production, they go to GCP Cloud Monitoring."
        }
    else:
        return {
            "status": "metrics_sent_to_gcp",
            "monitoring_url": f"https://console.cloud.google.com/monitoring/metrics-explorer"
        }


@router.post("/metrics/test")
def test_metrics(monitoring_service = Depends(get_monitoring_service)) -> Dict[str, str]:
    """Test endpoint to generate sample metrics"""
    
    # Test counter
    monitoring_service.client.record_counter("test_counter", 1.0, {"source": "api_test"})
    
    # Test gauge
    monitoring_service.client.record_gauge("test_gauge", 42.0, {"type": "sample"})
    
    # Test histogram
    monitoring_service.client.record_histogram("test_duration", 0.125, {"operation": "test"})
    
    # Test business metric
    monitoring_service.track_business_metric("api_test_runs", 1.0, {"endpoint": "/metrics/test"})
    
    return {"status": "test_metrics_recorded"}