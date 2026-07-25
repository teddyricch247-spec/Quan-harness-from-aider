from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/health")
def health_check():
    """فحص صحة الخدمة"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "aider-agent"
    }
