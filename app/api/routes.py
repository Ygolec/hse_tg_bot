import logging
from fastapi import APIRouter, FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from app.bot.notifications import send_notification

logger = logging.getLogger(__name__)

class NotificationRequest(BaseModel):
    user_id: int
    notification_type: str  # "checkin", "relocation", "general"
    message: str
    status: Optional[str] = None

router = APIRouter(prefix="/api", tags=["notifications"])

@router.post("/notify")
async def send_user_notification(notification: NotificationRequest):
    logger.info(f"Received notification request for user {notification.user_id}")
    
    try:

        result = send_notification(
            notification.user_id,
            notification.notification_type,
            notification.message,
            notification.status
        )
        
        return {"status": "success", "message": "Notification sent successfully"}
    
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

def setup_routes(app: FastAPI):
    app.include_router(router)
    logger.info("API routes registered")