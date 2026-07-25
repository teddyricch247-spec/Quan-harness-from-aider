from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RepositoryCreate(BaseModel):
    url: str = Field(..., description="رابط المستودع")
    branch: Optional[str] = Field("main", description="الفرع المطلوب")

class RepositoryUpdate(BaseModel):
    branch: Optional[str] = Field(None, description="تغيير الفرع")
    status: Optional[str] = Field(None, description="تحديث الحالة")

class RepositoryResponse(BaseModel):
    id: str
    url: str
    default_branch: str
    current_branch: Optional[str]
    local_path: str
    status: str
    last_pull_at: Optional[datetime]
    last_commit: Optional[str]
    created_at: datetime
    updated_at: datetime
