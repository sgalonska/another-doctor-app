"""
Upload and file serving endpoints
"""
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from starlette.responses import Response

from app.services.upload_service import upload_service

router = APIRouter()


@router.post("/presigned-url", response_model=Dict[str, Any])
async def generate_presigned_url(
    filename: str = Form(...),
    content_type: str = Form(...)
) -> Dict[str, Any]:
    """Generate presigned URL for file upload"""
    try:
        result = await upload_service.generate_presigned_url(filename, content_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/direct", response_model=Dict[str, str])
async def upload_file_direct(file: UploadFile = File(...)) -> Dict[str, str]:
    """Upload file directly to storage"""
    try:
        file_url = await upload_service.upload_file_direct(file)
        return {"url": file_url, "message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text", response_model=Dict[str, str])
async def process_text_content(
    content: str = Form(...),
    title: str = Form(...)
) -> Dict[str, str]:
    """Process text content and create a case"""
    try:
        case_id = await upload_service.process_text_content(content, title)
        return {"case_id": case_id, "message": "Text content processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{file_path:path}")
async def get_file_url(file_path: str, expiration_minutes: int = 60) -> Dict[str, str]:
    """Get file URL"""
    try:
        url = upload_service.get_file_url(file_path, expiration_minutes)
        if url:
            return {"url": url}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/file/{file_path:path}")
async def delete_file(file_path: str) -> Dict[str, str]:
    """Delete file"""
    try:
        success = upload_service.delete_file(file_path)
        if success:
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Local file serving for development
@router.get("/{file_path:path}")
async def serve_local_file(file_path: str):
    """Serve local files for development (only works when using LocalFileStorage)"""
    if not upload_service.is_local:
        raise HTTPException(status_code=404, detail="File serving only available in development")
    
    # Construct full file path
    uploads_dir = Path("uploads")
    full_path = uploads_dir / file_path
    
    # Security check - ensure the file is within the uploads directory
    try:
        full_path = full_path.resolve()
        uploads_dir = uploads_dir.resolve()
        
        if not str(full_path).startswith(str(uploads_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        if not full_path.is_file():
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Return the file
        return FileResponse(full_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")