from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
import uuid
from datetime import datetime

from ..database.database import db_service
from ..schemas.repository import RepositoryCreate, RepositoryUpdate, RepositoryResponse
from ..services.git_service import git_service
from ..services.workspace_service import workspace_service
from ..services.settings_service import settings_service

router = APIRouter(prefix="/repositories", tags=["repositories"])

@router.post("", response_model=RepositoryResponse, status_code=201)
def create_repository(
    body: RepositoryCreate,
    authorization: Optional[str] = Header(default=None)
):
    """إنشاء مستودع جديد (استنساخ)"""
    check_auth(authorization)
    
    repo_id = str(uuid.uuid4())
    repo_path = workspace_service.get_repo_path(repo_id)
    
    # إنشاء سجل في قاعدة البيانات
    conn = db_service.get_connection()
    conn.execute(
        """INSERT INTO repositories (id, url, default_branch, local_path, status)
           VALUES (?, ?, ?, ?, 'cloning')""",
        (repo_id, body.url, body.branch, str(repo_path))
    )
    conn.commit()
    
    try:
        # محاولة استنساخ المستودع
        success = git_service.clone(body.url, repo_path, body.branch)
        
        if success:
            # تحديث الحالة
            current_branch = git_service.get_current_branch(repo_path)
            last_commit = git_service.get_last_commit(repo_path)
            
            conn.execute(
                """UPDATE repositories 
                   SET status = 'ready', current_branch = ?, last_commit = ?, 
                       last_pull_at = ?, updated_at = ?
                   WHERE id = ?""",
                (current_branch, last_commit, datetime.utcnow().isoformat(), 
                 datetime.utcnow().isoformat(), repo_id)
            )
            conn.commit()
        else:
            raise Exception("Clone failed")
            
    except Exception as e:
        conn.execute(
            "UPDATE repositories SET status = 'failed', updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), repo_id)
        )
        conn.commit()
        raise HTTPException(status_code=500, detail=f"Failed to clone repository: {e}")
    
    return get_repository(repo_id)

@router.get("", response_model=List[RepositoryResponse])
def list_repositories(authorization: Optional[str] = Header(default=None)):
    """قائمة المستودعات"""
    check_auth(authorization)
    
    conn = db_service.get_connection()
    cursor = conn.execute("SELECT * FROM repositories ORDER BY created_at DESC")
    
    repositories = []
    for row in cursor:
        repositories.append(dict(row))
    
    return repositories

@router.get("/{repo_id}", response_model=RepositoryResponse)
def get_repository(repo_id: str, authorization: Optional[str] = Header(default=None)):
    """تفاصيل مستودع"""
    check_auth(authorization)
    
    conn = db_service.get_connection()
    cursor = conn.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
    repo = cursor.fetchone()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # تحديث معلومات الفرع والالتزام
    repo_path = Path(dict(repo)["local_path"])
    if repo_path.exists() and (repo_path / ".git").exists():
        current_branch = git_service.get_current_branch(repo_path)
        last_commit = git_service.get_last_commit(repo_path)
        
        conn.execute(
            "UPDATE repositories SET current_branch = ?, last_commit = ?, updated_at = ? WHERE id = ?",
            (current_branch, last_commit, datetime.utcnow().isoformat(), repo_id)
        )
        conn.commit()
    
    # إعادة قراءة البيانات المحدثة
    cursor = conn.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,))
    return dict(cursor.fetchone())

@router.patch("/{repo_id}", response_model=RepositoryResponse)
def update_repository(
    repo_id: str, 
    body: RepositoryUpdate,
    authorization: Optional[str] = Header(default=None)
):
    """تحديث مستودع"""
    check_auth(authorization)
    
    conn = db_service.get_connection()
    repo = conn.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,)).fetchone()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    updates = []
    params = []
    
    if body.branch:
        repo_path = workspace_service.get_repo_path(repo_id)
        git_service.pull(repo_path, body.branch)
        updates.append("current_branch = ?")
        params.append(body.branch)
    
    if body.status:
        if body.status not in ["pending", "cloning", "ready", "failed"]:
            raise HTTPException(status_code=400, detail="Invalid status")
        updates.append("status = ?")
        params.append(body.status)
    
    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(repo_id)
        
        conn.execute(
            f"UPDATE repositories SET {', '.join(updates)} WHERE id = ?",
            params
        )
        conn.commit()
    
    return get_repository(repo_id)

@router.delete("/{repo_id}")
def delete_repository(repo_id: str, authorization: Optional[str] = Header(default=None)):
    """حذف مستودع"""
    check_auth(authorization)
    
    conn = db_service.get_connection()
    repo = conn.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,)).fetchone()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # حذف المجلد
    workspace_service.delete_repo(repo_id)
    
    # حذف من قاعدة البيانات
    conn.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
    conn.commit()
    
    return {"message": "Repository deleted", "id": repo_id}
