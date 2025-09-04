"""
Dependency injection container for the application
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, BinaryIO
from fastapi import UploadFile
from datetime import datetime

from app.core.config import settings


# Abstract interfaces
class QueueClient(ABC):
    @abstractmethod
    def create_task(self, task_type: str, payload: Dict[str, Any], delay_seconds: int = 0) -> str:
        pass

    @abstractmethod
    def register_handler(self, task_type: str, handler):
        pass

    @abstractmethod
    def enqueue_diagnosis_analysis(self, case_id: str, file_path: str, user_id: str, delay_seconds: int = 0) -> str:
        pass

    @abstractmethod
    def enqueue_specialist_matching(self, case_id: str, diagnosis_data: Dict[str, Any], user_id: str, delay_seconds: int = 0) -> str:
        pass

    @abstractmethod
    def enqueue_notification(self, user_id: str, notification_type: str, data: Dict[str, Any], delay_seconds: int = 0) -> str:
        pass


class StorageClient(ABC):
    @abstractmethod
    async def generate_presigned_url(self, filename: str, content_type: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def upload_file_direct(self, file: UploadFile) -> str:
        pass

    @abstractmethod
    async def process_text_content(self, text_content: str, case_title: str) -> str:
        pass

    @abstractmethod
    def get_file_url(self, key: str) -> str:
        pass


# Service classes that accept dependencies via constructor
class QueueService:
    def __init__(self, client: QueueClient):
        self.client = client
        self.is_local = hasattr(client, 'tasks')  # LocalTaskEmulator has tasks attribute

    def get_task_status(self, task_id: str):
        if hasattr(self.client, 'get_task_status'):
            return self.client.get_task_status(task_id)
        return None


class UploadService:
    def __init__(self, storage: StorageClient):
        self.storage = storage
        self.is_local = hasattr(storage, 'uploads_dir')  # LocalFileStorage has uploads_dir attribute

    async def generate_presigned_url(self, filename: str, content_type: str) -> Dict[str, Any]:
        return await self.storage.generate_presigned_url(filename, content_type)

    async def upload_file_direct(self, file: UploadFile) -> str:
        return await self.storage.upload_file_direct(file)

    async def process_text_content(self, text_content: str, case_title: str) -> str:
        return await self.storage.process_text_content(text_content, case_title)

    def get_file_url(self, key: str) -> str:
        return self.storage.get_file_url(key)


# Dependency injection container
class DIContainer:
    def __init__(self):
        self._queue_service: Optional[QueueService] = None
        self._upload_service: Optional[UploadService] = None

    def get_queue_service(self) -> QueueService:
        if self._queue_service is None:
            if settings.ENVIRONMENT == "development":
                from app.services.queue_service import LocalTaskEmulator
                client = LocalTaskEmulator()
            else:
                from app.services.queue_service import GCPTasksClient
                client = GCPTasksClient()
            
            self._queue_service = QueueService(client)
        return self._queue_service

    def get_upload_service(self) -> UploadService:
        if self._upload_service is None:
            if settings.ENVIRONMENT == "development":
                from app.services.upload_service import LocalFileStorage
                storage = LocalFileStorage()
            else:
                from app.services.upload_service import GCPCloudStorage
                storage = GCPCloudStorage()
            
            self._upload_service = UploadService(storage)
        return self._upload_service


# Global container instance
container = DIContainer()


# FastAPI dependency functions
def get_queue_service() -> QueueService:
    return container.get_queue_service()


def get_upload_service() -> UploadService:
    return container.get_upload_service()