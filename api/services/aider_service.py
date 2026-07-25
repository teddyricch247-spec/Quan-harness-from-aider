from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from .git_service import git_service
from .process_service import process_service, ProcessInfo
from .workspace_service import workspace_service

class AiderService:
    def __init__(self):
        self._aider_command = "aider"
        self._default_model = "openai/gpt-4o-mini"

    def build_command(self,
                      message: str,
                      repo_path: Path,
                      model: Optional[str] = None,
                      files: Optional[List[str]] = None,
                      auto_commits: bool = True) -> List[str]:
        """بناء أمر Aider"""
        command = [
            self._aider_command,
            "--message", message,
            "--model", model or self._default_model,
            "--no-pretty"  # تنسيق مناسب للسجلات
        ]

        # إضافة الملفات المحددة
        if files:
            for file in files:
                command.extend(["--file", file])

        # الموافقة التلقائية
        if auto_commits:
            command.append("--yes-always")
        else:
            command.append("--yes")

        return command

    def start_job(self,
                  job_id: str,
                  message: str,
                  repo_path: Path,
                  model: Optional[str] = None,
                  files: Optional[List[str]] = None,
                  auto_commits: bool = True) -> ProcessInfo:
        """بدء مهمة Aider جديدة"""
        
        # التحقق من جاهزية المستودع
        if not git_service.is_repo_ready(repo_path):
            raise ValueError(f"Repository at {repo_path} is not ready")

        # التأكد من وجود هوية Git
        git_service.configure_identity(repo_path)

        # بناء الأمر
        command = self.build_command(
            message=message,
            repo_path=repo_path,
            model=model,
            files=files,
            auto_commits=auto_commits
        )

        # إنشاء ملف السجل
        log_path = workspace_service.get_log_path(job_id)

        # بدء العملية
        process_info = process_service.start_process(
            command=command,
            cwd=repo_path,
            job_id=job_id,
            log_path=log_path
        )

        return process_info

    def check_job(self, job_id: str) -> Dict:
        """التحقق من حالة مهمة Aider"""
        process_info = process_service.get_process_by_job(job_id)
        
        if not process_info:
            return {
                "job_id": job_id,
                "status": "not_found",
                "message": "No process found for this job"
            }

        finished, returncode = process_service.check_process(process_info.process_id)
        
        result = {
            "job_id": job_id,
            "process_id": process_info.process_id,
            "pid": process_info.pid,
            "started_at": process_info.started_at.isoformat(),
            "log_path": str(process_info.log_path)
        }

        if finished:
            result["status"] = "completed" if returncode == 0 else "failed"
            result["return_code"] = returncode
            result["finished_at"] = datetime.utcnow().isoformat()
        else:
            result["status"] = "running"

        return result

    def cancel_job(self, job_id: str, force: bool = False) -> bool:
        """إلغاء مهمة Aider"""
        process_info = process_service.get_process_by_job(job_id)
        if not process_info:
            return False
        
        return process_service.stop_process(process_info.process_id, force=force)

    def get_job_logs(self, job_id: str) -> Optional[str]:
        """الحصول على سجلات مهمة Aider"""
        log_path = workspace_service.get_log_path(job_id)
        
        if not log_path.exists():
            return None
        
        try:
            return log_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

    def get_version(self) -> str:
        """الحصول على إصدار Aider"""
        import subprocess
        try:
            result = subprocess.run(
                [self._aider_command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception as e:
            return f"Error getting version: {e}"

    def validate_model(self, model: str) -> bool:
        """التحقق من صحة اسم النموذج"""
        # يمكن توسيعها للتحقق من النماذج المدعومة
        valid_prefixes = [
            "openai/", "anthropic/", "gemini/",
            "ollama/", "openrouter/"
        ]
        
        if "/" not in model:
            return False
        
        prefix = model.split("/")[0] + "/"
        return prefix in valid_prefixes

    def estimate_tokens(self, message: str) -> int:
        """تقدير عدد الرموز في الرسالة (تقريبي)"""
        # تقدير تقريبي: 4 أحرف = 1 رمز تقريباً
        return len(message) // 4

# نسخة عالمية
aider_service = AiderService()
