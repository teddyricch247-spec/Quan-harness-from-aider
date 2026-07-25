from fastapi import APIRouter
import sys
import subprocess
from ..services.aider_service import aider_service

router = APIRouter()

@router.get("/version")
def get_version():
    """معلومات إصدار الخدمة"""
    # إصدار Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # إصدار Git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
        git_version = result.stdout.strip().replace("git version ", "")
    except:
        git_version = "unknown"
    
    return {
        "service_version": "1.0.0",
        "aider_version": aider_service.get_version(),
        "python_version": python_version,
        "git_version": git_version,
        "status": "ok"
    }
