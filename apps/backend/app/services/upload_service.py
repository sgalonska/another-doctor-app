"""
File upload service with GCP Cloud Storage and local development emulation
"""
import os
import uuid
import shutil
import logging
from typing import Optional, BinaryIO, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import UploadFile

from app.core.config import settings
from app.core.dependencies import StorageClient

logger = logging.getLogger(__name__)


class LocalFileStorage(StorageClient):
    """Local file storage emulator for development"""
    
    def __init__(self):
        # Create local uploads directory
        self.uploads_dir = Path("uploads")
        self.uploads_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.uploads_dir / "diagnoses").mkdir(exist_ok=True)
        (self.uploads_dir / "cases").mkdir(exist_ok=True)
        (self.uploads_dir / "uploads").mkdir(exist_ok=True)
        (self.uploads_dir / "temp").mkdir(exist_ok=True)
        (self.uploads_dir / "processed").mkdir(exist_ok=True)
        
        logger.info(f"Local file storage initialized at: {self.uploads_dir.absolute()}")
    
    async def generate_presigned_url(self, filename: str, content_type: str) -> Dict[str, Any]:
        """Generate local 'presigned' URL for development"""
        key = f"uploads/{uuid.uuid4()}/{filename}"
        
        # For local development, return a mock presigned URL structure
        return {
            'upload_url': f"http://localhost:8000/api/upload/direct/{key.replace('/', '%2F')}",
            'key': key,
            'expires_in': 3600
        }
    
    async def upload_file_direct(self, file: UploadFile) -> str:
        """Upload file directly to local storage"""
        key = f"uploads/{uuid.uuid4()}/{file.filename}"
        
        try:
            # Create directory structure
            file_path = self.uploads_dir / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"File uploaded locally: {key}")
            
            # Return local file URL
            return f"http://localhost:8000/uploads/{key}"
            
        except Exception as e:
            logger.error(f"Error uploading file locally: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def process_text_content(self, text_content: str, case_title: str) -> str:
        """Process text content locally"""
        case_id = str(uuid.uuid4())
        key = f"cases/{case_id}/input.txt"
        
        try:
            # Create directory and file
            file_path = self.uploads_dir / key
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(text_content)
            
            # Store metadata in a separate file
            metadata_path = self.uploads_dir / f"cases/{case_id}/metadata.json"
            import json
            with open(metadata_path, 'w') as f:
                json.dump({
                    'case_id': case_id,
                    'title': case_title,
                    'created_at': datetime.now().isoformat(),
                    'content_type': 'text/plain'
                }, f)
            
            logger.info(f"Text content processed locally for case: {case_id}")
            return case_id
            
        except Exception as e:
            logger.error(f"Error processing text content locally: {e}")
            raise Exception(f"Failed to process text content: {str(e)}")
    
    def get_file_url(self, key: str, expiration_minutes: int = 60) -> Optional[str]:
        """Get local file URL"""
        file_path = self.uploads_dir / key
        if file_path.exists():
            return f"http://localhost:8000/uploads/{key}"
        return None
    
    def delete_file(self, key: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = self.uploads_dir / key
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted locally: {key}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting local file {key}: {e}")
            return False


class GCPCloudStorage(StorageClient):
    """Production GCP Cloud Storage client"""
    
    def __init__(self):
        try:
            from google.cloud import storage
            from google.api_core import exceptions
            
            self.client = storage.Client(project=settings.GCP_PROJECT_ID)
            self.bucket_name = settings.GCS_BUCKET_NAME
            self.bucket = self.client.bucket(self.bucket_name)
            self.exceptions = exceptions
            
            logger.info(f"Connected to GCS bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to connect to GCS bucket {self.bucket_name}: {e}")
            raise
    
    async def generate_presigned_url(self, filename: str, content_type: str) -> Dict[str, Any]:
        """Generate presigned URL for direct upload to GCS"""
        key = f"uploads/{uuid.uuid4()}/{filename}"
        
        try:
            blob = self.bucket.blob(key)
            
            presigned_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(hours=1),
                method="PUT",
                content_type=content_type
            )
            
            return {
                'upload_url': presigned_url,
                'key': key,
                'expires_in': 3600
            }
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    async def upload_file_direct(self, file: UploadFile) -> str:
        """Upload file directly to GCS"""
        key = f"uploads/{uuid.uuid4()}/{file.filename}"
        
        try:
            file_content = await file.read()
            
            blob = self.bucket.blob(key)
            
            blob.upload_from_string(
                file_content,
                content_type=file.content_type or 'application/octet-stream'
            )
            
            logger.info(f"File uploaded to GCS: {key}")
            return f"https://storage.googleapis.com/{self.bucket_name}/{key}"
            
        except Exception as e:
            logger.error(f"Error uploading file to GCS: {e}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def process_text_content(self, text_content: str, case_title: str) -> str:
        """Process text content and store in GCS"""
        case_id = str(uuid.uuid4())
        key = f"cases/{case_id}/input.txt"
        
        try:
            blob = self.bucket.blob(key)
            
            blob.metadata = {
                'case_id': case_id,
                'title': case_title,
                'created_at': datetime.now().isoformat()
            }
            
            blob.upload_from_string(
                text_content,
                content_type='text/plain'
            )
            
            logger.info(f"Text content processed for case: {case_id}")
            return case_id
            
        except Exception as e:
            logger.error(f"Error processing text content in GCS: {e}")
            raise Exception(f"Failed to process text content: {str(e)}")
    
    def get_file_url(self, key: str, expiration_minutes: int = 60) -> Optional[str]:
        """Get signed URL for file"""
        try:
            blob = self.bucket.blob(key)
            
            if not blob.exists():
                return None
            
            url = blob.generate_signed_url(
                expiration=timedelta(minutes=expiration_minutes),
                method="GET"
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Error generating signed URL for {key}: {e}")
            return None
    
    def delete_file(self, key: str) -> bool:
        """Delete file from GCS"""
        try:
            blob = self.bucket.blob(key)
            blob.delete()
            logger.info(f"File deleted from GCS: {key}")
            return True
            
        except self.exceptions.NotFound:
            logger.warning(f"File not found in GCS: {key}")
            return False
        except Exception as e:
            logger.error(f"Error deleting file from GCS: {e}")
            return False


# Global instance (for backward compatibility)
# This will be replaced by dependency injection in endpoints
if settings.ENVIRONMENT == "development":
    upload_service = LocalFileStorage()
else:
    upload_service = GCPCloudStorage()