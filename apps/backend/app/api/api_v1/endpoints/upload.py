from typing import Any
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.services.upload_service import UploadService

router = APIRouter()

@router.post("/presigned-url")
async def get_presigned_url(
    filename: str = Form(...),
    content_type: str = Form(...),
) -> Any:
    """
    Get presigned URL for file upload to R2.
    """
    upload_service = UploadService()
    try:
        presigned_data = await upload_service.generate_presigned_url(filename, content_type)
        return presigned_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/direct")
async def upload_file_direct(
    file: UploadFile = File(...),
) -> Any:
    """
    Direct file upload (fallback for presigned URL failures).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    upload_service = UploadService()
    try:
        file_url = await upload_service.upload_file_direct(file)
        return {"file_url": file_url, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text")
async def upload_text(
    text_content: str = Form(...),
    case_title: str = Form(default="Patient Case"),
) -> Any:
    """
    Upload medical text directly (no file).
    """
    if not text_content.strip():
        raise HTTPException(status_code=400, detail="No text content provided")
    
    # Process the text content
    upload_service = UploadService()
    try:
        case_id = await upload_service.process_text_content(text_content, case_title)
        return {"case_id": case_id, "status": "processing"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))