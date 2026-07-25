from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class JobCreate(BaseModel):
    repository_id: str = Field(..., description="معرف المستودع")
    message: str = Field(..., description="الرسالة المرسلة لـ Aider")
    model: Optional[str] = Field(None, description="النموذج المستخدم")
    files: Optional[List[str]] = Field(None, description="ملفات محددة للتعديل")
    auto_commits: Optional[bool] = Field(True, description="التزام تلقائي")

class JobResponse(BaseModel):
    id: str
    repository_id: str
    message: str
    model: str
    status: str
    pid: Optional[int]
    exit_code: Optional[int]
    log_path: Optional[str]
    error_message: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class JobLogResponse(BaseModel):
    job_id: str
    logs: str
