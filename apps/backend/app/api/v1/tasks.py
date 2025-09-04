"""
Task processing endpoints
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.queue_service import queue_service, TaskResult

router = APIRouter()


class TaskRequest(BaseModel):
    task_type: str
    payload: Dict[str, Any]
    delay_seconds: int = 0


class TaskResponse(BaseModel):
    task_id: str
    message: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None


@router.post("/create", response_model=TaskResponse)
async def create_task(task_request: TaskRequest) -> TaskResponse:
    """Create a new background task"""
    try:
        task_id = queue_service.client.create_task(
            task_type=task_request.task_type,
            payload=task_request.payload,
            delay_seconds=task_request.delay_seconds
        )
        
        return TaskResponse(
            task_id=task_id,
            message=f"Task {task_id} created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get task status and result (only available in development)"""
    if not queue_service.is_local:
        raise HTTPException(
            status_code=404, 
            detail="Task status only available in development mode"
        )
    
    task_result = queue_service.get_task_status(task_id)
    
    if not task_result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        task_id=task_result.task_id,
        status=task_result.status,
        created_at=task_result.created_at.isoformat(),
        completed_at=task_result.completed_at.isoformat() if task_result.completed_at else None,
        result=task_result.result,
        error=task_result.error
    )


@router.post("/diagnosis/analyze", response_model=TaskResponse)
async def analyze_diagnosis(
    case_id: str,
    file_path: str,
    user_id: str,
    delay_seconds: int = 0
) -> TaskResponse:
    """Queue a diagnosis analysis task"""
    try:
        task_id = queue_service.enqueue_diagnosis_analysis(
            case_id=case_id,
            file_path=file_path,
            user_id=user_id,
            delay_seconds=delay_seconds
        )
        
        return TaskResponse(
            task_id=task_id,
            message=f"Diagnosis analysis task {task_id} queued for case {case_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/specialist/match", response_model=TaskResponse)
async def match_specialists(
    case_id: str,
    diagnosis_data: Dict[str, Any],
    user_id: str,
    delay_seconds: int = 0
) -> TaskResponse:
    """Queue a specialist matching task"""
    try:
        task_id = queue_service.enqueue_specialist_matching(
            case_id=case_id,
            diagnosis_data=diagnosis_data,
            user_id=user_id,
            delay_seconds=delay_seconds
        )
        
        return TaskResponse(
            task_id=task_id,
            message=f"Specialist matching task {task_id} queued for case {case_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notification/send", response_model=TaskResponse)
async def send_notification(
    user_id: str,
    notification_type: str,
    data: Dict[str, Any],
    delay_seconds: int = 0
) -> TaskResponse:
    """Queue a notification task"""
    try:
        task_id = queue_service.enqueue_notification(
            user_id=user_id,
            notification_type=notification_type,
            data=data,
            delay_seconds=delay_seconds
        )
        
        return TaskResponse(
            task_id=task_id,
            message=f"Notification task {task_id} queued for user {user_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process", include_in_schema=False)
async def process_task(task_data: Dict[str, Any]):
    """
    Internal endpoint for GCP Cloud Tasks to process tasks
    This endpoint is only used in production when GCP calls back
    """
    task_type = task_data.get('type')
    payload = task_data.get('payload', {})
    
    if not task_type:
        raise HTTPException(status_code=400, detail="Task type is required")
    
    try:
        # Import task handlers
        from app.services.task_handlers import (
            handle_diagnosis_analysis,
            handle_specialist_matching,
            handle_notification
        )
        
        handlers = {
            'diagnosis_analysis': handle_diagnosis_analysis,
            'specialist_matching': handle_specialist_matching,
            'notification': handle_notification
        }
        
        handler = handlers.get(task_type)
        if not handler:
            raise HTTPException(status_code=400, detail=f"Unknown task type: {task_type}")
        
        result = handler(payload)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))