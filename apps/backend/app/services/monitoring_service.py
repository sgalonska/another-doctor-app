"""
Monitoring service with GCP Cloud Monitoring integration and local logging.
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class MetricData:
    name: str
    value: float
    labels: Optional[Dict[str, str]] = None
    timestamp: Optional[datetime] = None

class MonitoringClient(ABC):
    """Abstract monitoring client interface"""
    
    @abstractmethod
    def record_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        """Record a counter metric"""
        pass
    
    @abstractmethod
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a gauge metric"""
        pass
    
    @abstractmethod
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram metric (for timing, etc.)"""
        pass
    
    @abstractmethod
    def record_error(self, error_type: str, endpoint: str, details: Optional[str] = None):
        """Record an error occurrence"""
        pass
    
    @abstractmethod
    def start_timer(self, operation: str) -> Any:
        """Start timing an operation"""
        pass
    
    @abstractmethod
    def end_timer(self, timer: Any, labels: Optional[Dict[str, str]] = None):
        """End timing an operation"""
        pass


class LocalMonitoringClient(MonitoringClient):
    """Local monitoring client with basic logging"""
    
    def __init__(self):
        self.logger = logging.getLogger("monitoring")
        self.logger.setLevel(logging.INFO)
        
        # Ensure we have a handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - METRICS - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def record_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        labels_str = f" {labels}" if labels else ""
        self.logger.info(f"COUNTER {name}={value}{labels_str}")
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        labels_str = f" {labels}" if labels else ""
        self.logger.info(f"GAUGE {name}={value}{labels_str}")
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        labels_str = f" {labels}" if labels else ""
        self.logger.info(f"HISTOGRAM {name}={value:.3f}s{labels_str}")
    
    def record_error(self, error_type: str, endpoint: str, details: Optional[str] = None):
        details_str = f" - {details}" if details else ""
        self.logger.error(f"ERROR {error_type} at {endpoint}{details_str}")
    
    def start_timer(self, operation: str) -> Dict[str, Any]:
        return {
            "operation": operation,
            "start_time": time.time()
        }
    
    def end_timer(self, timer: Dict[str, Any], labels: Optional[Dict[str, str]] = None):
        duration = time.time() - timer["start_time"]
        operation = timer["operation"]
        self.record_histogram(f"{operation}_duration", duration, labels)


class GCPMonitoringClient(MonitoringClient):
    """GCP Cloud Monitoring client"""
    
    def __init__(self):
        try:
            from google.cloud import monitoring_v3
            self.client = monitoring_v3.MetricServiceClient()
            self.project_id = settings.GCP_PROJECT_ID
            self.project_name = f"projects/{self.project_id}"
            logger.info("Initialized GCP Cloud Monitoring client")
        except Exception as e:
            logger.error(f"Failed to initialize GCP Monitoring client: {e}")
            raise
    
    def _create_time_series(self, metric_type: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Helper to create a time series for GCP monitoring"""
        try:
            from google.cloud import monitoring_v3
            from google.cloud.monitoring_v3 import TimeSeries, Point, TimeInterval
            from google.protobuf import timestamp_pb2
            import time as time_module
            
            # Create time series
            series = TimeSeries()
            series.metric.type = f"custom.googleapis.com/{metric_type}"
            series.resource.type = "global"
            
            # Add labels if provided
            if labels:
                for key, val in labels.items():
                    series.metric.labels[key] = str(val)
            
            # Create time interval
            now = time_module.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            
            interval = TimeInterval()
            interval.end_time.seconds = seconds
            interval.end_time.nanos = nanos
            
            # Create point
            point = Point()
            point.value.double_value = value
            point.interval = interval
            
            series.points = [point]
            
            # Send to GCP
            self.client.create_time_series(
                name=self.project_name,
                time_series=[series]
            )
            
        except Exception as e:
            logger.error(f"Failed to send metric to GCP: {e}")
    
    def record_counter(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None):
        self._create_time_series(f"counter/{name}", value, labels)
    
    def record_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        self._create_time_series(f"gauge/{name}", value, labels)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        self._create_time_series(f"histogram/{name}", value, labels)
    
    def record_error(self, error_type: str, endpoint: str, details: Optional[str] = None):
        labels = {
            "error_type": error_type,
            "endpoint": endpoint
        }
        if details:
            labels["details"] = details[:100]  # Limit label size
        
        self.record_counter("errors_total", 1.0, labels)
    
    def start_timer(self, operation: str) -> Dict[str, Any]:
        return {
            "operation": operation,
            "start_time": time.time()
        }
    
    def end_timer(self, timer: Dict[str, Any], labels: Optional[Dict[str, str]] = None):
        duration = time.time() - timer["start_time"]
        operation = timer["operation"]
        self.record_histogram(f"{operation}_duration", duration, labels)


class MonitoringService:
    """Main monitoring service with dependency injection"""
    
    def __init__(self, client: MonitoringClient):
        self.client = client
        self.is_local = isinstance(client, LocalMonitoringClient)
    
    def track_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Track HTTP request metrics"""
        labels = {
            "method": method,
            "endpoint": endpoint,
            "status_code": str(status_code)
        }
        
        # Record request count
        self.client.record_counter("http_requests_total", 1.0, labels)
        
        # Record request duration
        self.client.record_histogram("http_request_duration", duration, labels)
        
        # Record errors if status >= 400
        if status_code >= 400:
            error_type = "client_error" if status_code < 500 else "server_error"
            self.client.record_error(error_type, endpoint)
    
    def track_database_query(self, operation: str, duration: float, success: bool = True):
        """Track database query metrics"""
        labels = {
            "operation": operation,
            "status": "success" if success else "error"
        }
        
        self.client.record_counter("db_queries_total", 1.0, labels)
        self.client.record_histogram("db_query_duration", duration, labels)
    
    def track_external_api_call(self, service: str, endpoint: str, duration: float, success: bool = True):
        """Track external API call metrics"""
        labels = {
            "service": service,
            "endpoint": endpoint,
            "status": "success" if success else "error"
        }
        
        self.client.record_counter("external_api_calls_total", 1.0, labels)
        self.client.record_histogram("external_api_duration", duration, labels)
    
    def track_business_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Track custom business metrics"""
        self.client.record_gauge(f"business_{name}", value, labels)
    
    def start_operation_timer(self, operation: str) -> Any:
        """Start timing an operation"""
        return self.client.start_timer(operation)
    
    def end_operation_timer(self, timer: Any, labels: Optional[Dict[str, str]] = None):
        """End timing an operation"""
        self.client.end_timer(timer, labels)


# Global instance removed - now using dependency injection via app.core.dependencies