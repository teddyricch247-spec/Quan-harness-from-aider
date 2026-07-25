from fastapi import HTTPException, Header
from typing import Optional
import os

def check_auth(authorization: Optional[str] = None):
    """التحقق من المصادقة"""
    api_token = os.getenv("AGENT_API_TOKEN")
    
    # إذا لم يتم تعيين رمز، نسمح بالوصول (للتطوير)
    if not api_token:
        return
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    expected = f"Bearer {api_token}"
    if authorization != expected:
        raise HTTPException(status_code=403, detail="Invalid token")
