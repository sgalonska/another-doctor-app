"""
Queue service for handling background tasks with GCP Cloud Tasks.
For localhost development, tasks are executed synchronously.
"""
import json
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass

from app.core.config import settings
from app.core.dependencies import QueueClient

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    task_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None

class LocalTaskEmulator(QueueClient):
    """Local emulator for Cloud Tasks that executes tasks synchronously"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskResult] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.task_counter = 0
    
    def register_handler(self, task_type: str, handler: Callable):
        """Register a handler function for a specific task type"""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    def create_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        delay_seconds: int = 0
    ) -> str:
        """Create and immediately execute a task (for localhost)"""
        self.task_counter += 1
        task_id = f"local_task_{self.task_counter}_{int(datetime.now().timestamp())}"
        
        task_result = TaskResult(
            task_id=task_id,
            status='running',
            created_at=datetime.now()
        )
        
        self.tasks[task_id] = task_result
        logger.info(f"Created task {task_id} of type {task_type}")
        
        try:
            if task_type not in self.task_handlers:
                raise ValueError(f"No handler registered for task type: {task_type}")
            
            handler = self.task_handlers[task_type]
            result = handler(payload)
            
            task_result.status = 'completed'
            task_result.completed_at = datetime.now()
            task_result.result = result
            
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            task_result.status = 'failed'
            task_result.completed_at = datetime.now()
            task_result.error = str(e)
            
            logger.error(f"Task {task_id} failed: {e}")
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """Get task status and result"""
        return self.tasks.get(task_id)
    
    def enqueue_diagnosis_analysis(self, case_id: str, file_path: str, user_id: str, delay_seconds: int = 0) -> str:
        """Enqueue a diagnosis analysis task"""
        payload = {
            'case_id': case_id,
            'file_path': file_path,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        return self.create_task('diagnosis_analysis', payload, delay_seconds)
    
    def enqueue_specialist_matching(self, case_id: str, diagnosis_data: Dict[str, Any], user_id: str, delay_seconds: int = 0) -> str:
        """Enqueue a specialist matching task"""
        payload = {
            'case_id': case_id,
            'diagnosis_data': diagnosis_data,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        return self.create_task('specialist_matching', payload, delay_seconds)
    
    def enqueue_notification(self, user_id: str, notification_type: str, data: Dict[str, Any], delay_seconds: int = 0) -> str:
        """Enqueue a notification task"""
        payload = {
            'user_id': user_id,
            'notification_type': notification_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        return self.create_task('notification', payload, delay_seconds)

class GCPTasksClient(QueueClient):
    """Production GCP Cloud Tasks client"""
    
    def __init__(self):
        try:
            from google.cloud import tasks_v2
            self.client = tasks_v2.CloudTasksClient()
            self.parent = self.client.queue_path(
                settings.GCP_PROJECT_ID,
                settings.GCP_LOCATION, 
                settings.GCP_TASK_QUEUE_NAME
            )
            logger.info("Initialized GCP Cloud Tasks client")
        except Exception as e:
            logger.error(f"Failed to initialize GCP Tasks client: {e}")
            raise
    
    def create_task(
        self,
        task_type: str,
        payload: Dict[str, Any],
        delay_seconds: int = 0,
        endpoint: str = "/tasks/process"
    ) -> str:
        """Create a task in GCP Cloud Tasks"""
        try:
            from google.cloud import tasks_v2
            from google.protobuf import timestamp_pb2
            import time
            
            task_data = {
                'type': task_type,
                'payload': payload
            }
            
            task = {
                'http_request': {
                    'http_method': tasks_v2.HttpMethod.POST,
                    'url': f"{settings.SERVER_HOST}{endpoint}",
                    'headers': {
                        'Content-Type': 'application/json',
                    },
                    'body': json.dumps(task_data).encode(),
                }
            }
            
            if delay_seconds > 0:
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromSeconds(int(time.time() + delay_seconds))
                task['schedule_time'] = timestamp
            
            response = self.client.create_task(parent=self.parent, task=task)
            task_id = response.name.split('/')[-1]
            
            logger.info(f"Created GCP task {task_id} of type {task_type}")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create GCP task: {e}")
            raise
    
    def register_handler(self, task_type: str, handler):
        """GCP doesn't need to register handlers - tasks are processed via HTTP endpoints"""
        pass
    
    def enqueue_diagnosis_analysis(self, case_id: str, file_path: str, user_id: str, delay_seconds: int = 0) -> str:
        """Enqueue a diagnosis analysis task"""
        payload = {
            'case_id': case_id,
            'file_path': file_path,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        return self.create_task('diagnosis_analysis', payload, delay_seconds)
    
    def enqueue_specialist_matching(self, case_id: str, diagnosis_data: Dict[str, Any], user_id: str, delay_seconds: int = 0) -> str:
        """Enqueue a specialist matching task"""
        payload = {
            'case_id': case_id,
            'diagnosis_data': diagnosis_data,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        }
        return self.create_task('specialist_matching', payload, delay_seconds)
    
    def enqueue_notification(self, user_id: str, notification_type: str, data: Dict[str, Any], delay_seconds: int = 0) -> str:
        """Enqueue a notification task"""
        payload = {
            'user_id': user_id,
            'notification_type': notification_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        return self.create_task('notification', payload, delay_seconds)

# Global instance removed - now using dependency injection via app.core.dependencies