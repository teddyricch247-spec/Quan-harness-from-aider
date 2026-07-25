from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
from typing import Optional, List
import uuid
from datetime import datetime

from ..database.database import db_service
from ..schemas.job import JobCreate, JobResponse, JobLogResponse
from ..services.aider_service import aider_service
from ..services.workspace_service import workspace_service
from ..services.log_service import log_service

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("", response_model=JobResponse, status_code=201)
def create_job(
    body: JobCreate,
    authorization: Optional[str] = Header(default=None)
):
    """إنشاء مهمة Aider جديدة"""
    check_auth(authorization)
    
    # التحقق من وجود المستودع
    conn = db_service.get_connection()
    repo = conn.execute(
        "SELECT * FROM repositories WHERE id = ? AND status = 'ready'",
        (body.repository_id,)
    ).fetchone()
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or not ready")
    
    job_id = str(uuid.uuid4())
    repo_path = workspace_service.get_repo_path(body.repository_id)
    log_path = workspace_service.get_log_path(job_id)
    model = body.model or "openai/gpt-4o-mini"
    
    # إنشاء سجل المهمة في قاعدة البيانات
    conn.execute(
        """INSERT INTO jobs (id, repository_id, message, model, status, log_path, created_at, updated_at)
           VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)""",
        (job_id, body.repository_id, body.message, model, str(log_path),
         datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
    )
    conn.execute(
        "INSERT INTO job_events (job_id, event, details) VALUES (?, 'pending', 'Job created')",
        (job_id,)
    )
    conn.commit()
    
    try:
        # بدء مهمة Aider
        process_info = aider_service.start_job(
            job_id=job_id,
            message=body.message,
            repo_path=repo_path,
            model=model,
            files=body.files,
            auto_commits=body.auto_commits
        )
        
        # تحديث حالة المهمة
        conn.execute(
            """UPDATE jobs 
               SET status = 'running', pid = ?, started_at = ?, updated_at = ?
               WHERE id = ?""",
            (process_info.pid, datetime.utcnow().isoformat(), 
             datetime.utcnow().isoformat(), job_id)
        )
        conn.execute(
            "INSERT INTO job_events (job_id, event, details) VALUES (?, 'running', ?)",
            (job_id, f"Process started with PID {process_info.pid}")
        )
        conn.commit()
        
    except Exception as e:
        conn.execute(
            """UPDATE jobs 
               SET status = 'failed', error_message = ?, updated_at = ?
               WHERE id = ?""",
            (str(e), datetime.utcnow().isoformat(), job_id)
        )
        conn.execute(
            "INSERT INTO job_events (job_id, event, details) VALUES (?, 'failed', ?)",
            (job_id, str(e))
        )
        conn.commit()
        raise HTTPException(status_code=500, detail=f"Failed to start job: {e}")
    
    cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    return dict(cursor.fetchone())

@router.get("", response_model=List[JobResponse])
def list_jobs(authorization: Optional[str] = Header(default=None)):
    """قائمة المهام"""
    check_auth(authorization)
    
    conn = db_service.get_connection()
    cursor = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50")
    
    jobs = []
    for row in cursor:
        jobs.append(dict(row))
    
    return jobs

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, authorization: Optional[str] = Header(default=None)):
    """تفاصيل مهمة"""
    check_auth(authorization)
    
    conn = db_service.get_connection()
    
    # التحقق من حالة العملية
    process_info = aider_service.check_job(job_id)
    
    if process_info.get("status") == "completed":
        conn.execute(
            "UPDATE jobs SET status = 'completed', exit_code = 0, finished_at = ?, updated_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), job_id)
        )
        conn.execute(
            "INSERT INTO job_events (job_id, event, details) VALUES (?, 'completed', 'Job completed successfully')",
            (job_id,)
        )
    elif process_info.get("status") == "failed":
        conn.execute(
            "UPDATE jobs SET status = 'failed', exit_code = ?, finished_at = ?, updated_at = ? WHERE id = ?",
            (process_info.get("return_code", 1), datetime.utcnow().isoformat(), 
             datetime.utcnow().isoformat(), job_id)
        )
        conn.execute(
            "INSERT INTO job_events (job_id, event, details) VALUES (?, 'failed', ?)",
            (job_id, f"Job failed with exit code {process_info.get('return_code')}")
        )
    
    conn.commit()
    
    cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return dict(job)

@router.get("/{job_id}/logs", response_model=JobLogResponse)
def get_job_logs(job_id: str, authorization: Optional[str] = Header(default=None)):
    """سجلات مهمة"""
    check_auth(authorization)
    
    logs = log_service.get_log(job_id)
    
    if logs is None:
        raise HTTPException(status_code=404, detail="Logs not found")
    
    return {"job_id": job_id, "logs": logs}

@router.post("/{job_id}/cancel")
def cancel_job(job_id: str, force: bool = False, authorization: Optional[str] = Header(default=None)):
    """إلغاء مهمة"""
    check_auth(authorization)
    
    success = aider_service.cancel_job(job_id, force=force)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or already completed")
    
    conn = db_service.get_connection()
    conn.execute(
        "UPDATE jobs SET status = 'cancelled', finished_at = ?, updated_at = ? WHERE id = ?",
        (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), job_id)
    )
    conn.execute(
        "INSERT INTO job_events (job_id, event, details) VALUES (?, 'cancelled', ?)",
        (job_id, "Cancelled by user")
    )
    conn.commit()
    
    return {"message": "Job cancelled", "job_id": job_id}

@router.get("/{job_id}/stream")
def stream_job(job_id: str, authorization: Optional[str] = Header(default=None)):
    """بث سجل المهمة (غير مطبق بعد)"""
    check_auth(authorization)
    
    # حالياً يرجع 501 Not Implemented
    raise HTTPException(status_code=501, detail="Streaming not implemented yet")
