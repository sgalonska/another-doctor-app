import uuid
from typing import Optional
from fastapi import UploadFile
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

class UploadService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            region_name='auto'  # Cloudflare R2 uses 'auto'
        )
        self.bucket_name = settings.R2_BUCKET_NAME

    async def generate_presigned_url(self, filename: str, content_type: str) -> dict:
        """Generate presigned URL for direct upload to R2."""
        key = f"uploads/{uuid.uuid4()}/{filename}"
        
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                    'ContentType': content_type
                },
                ExpiresIn=3600  # 1 hour
            )
            
            return {
                'upload_url': presigned_url,
                'key': key,
                'expires_in': 3600
            }
        except ClientError as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    async def upload_file_direct(self, file: UploadFile) -> str:
        """Upload file directly to R2."""
        key = f"uploads/{uuid.uuid4()}/{file.filename}"
        
        try:
            file_content = await file.read()
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=file_content,
                ContentType=file.content_type or 'application/octet-stream'
            )
            
            # Return the URL to access the file
            return f"{settings.R2_ENDPOINT_URL}/{self.bucket_name}/{key}"
            
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    async def process_text_content(self, text_content: str, case_title: str) -> str:
        """Process text content and create a case."""
        # Generate a case ID
        case_id = str(uuid.uuid4())
        
        # Store text in R2 for processing
        key = f"cases/{case_id}/input.txt"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=text_content.encode('utf-8'),
                ContentType='text/plain',
                Metadata={
                    'case_id': case_id,
                    'title': case_title
                }
            )
            
            # TODO: Queue processing job
            # queue_case_processing(case_id, key)
            
            return case_id
            
        except ClientError as e:
            raise Exception(f"Failed to process text content: {str(e)}")