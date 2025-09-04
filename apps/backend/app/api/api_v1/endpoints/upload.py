from typing import Any
from pathlib import Path
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Depends
from fastapi.responses import JSONResponse, FileResponse

from app.core.dependencies import get_upload_service, UploadService

router = APIRouter()

@router.post("/presigned-url")
async def get_presigned_url(
    filename: str = Form(...),
    content_type: str = Form(...),
    upload_service: UploadService = Depends(get_upload_service)
) -> Any:
    """
    Get presigned URL for file upload.
    """
    try:
        presigned_data = await upload_service.generate_presigned_url(filename, content_type)
        return presigned_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/direct")
async def upload_file_direct(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service)
) -> Any:
    """
    Direct file upload (fallback for presigned URL failures).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    try:
        file_url = await upload_service.upload_file_direct(file)
        return {"file_url": file_url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text")
async def upload_text(
    text_content: str = Form(...),
    case_title: str = Form(default="Patient Case"),
    upload_service: UploadService = Depends(get_upload_service)
) -> Any:
    """
    Upload medical text directly (no file).
    """
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="No text content provided")
    
    # Process the text content
    try:
        case_id = await upload_service.process_text_content(text_content, case_title)
        return {"case_id": case_id, "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Local file serving for development
@router.get("/{file_path:path}")
async def serve_local_file(
    file_path: str,
    upload_service: UploadService = Depends(get_upload_service)
):
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