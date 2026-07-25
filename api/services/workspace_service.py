import os
import shutil
from pathlib import Path
from typing import Optional


class WorkspaceService:
    """
    إدارة مساحة العمل والمجلدات.
    تقرأ WORKSPACE_DIR من متغير البيئة مباشرة لتجنب الاعتماد على SettingsService
    الذي يحتاج قاعدة بيانات مهيأة مسبقاً.
    """

    def __init__(self):
        self._workspace_root: Optional[Path] = None

    @property
    def workspace_root(self) -> Path:
        """المسار الجذر لمساحة العمل - لا يعتمد على أي خدمة أخرى"""
        if not self._workspace_root:
            ws_path = os.getenv("WORKSPACE_DIR", "/workspace")
            self._workspace_root = Path(ws_path).resolve()
        return self._workspace_root

    @property
    def repos_dir(self) -> Path:
        """مجلد المستودعات"""
        return self.workspace_root / "repos"

    @property
    def logs_dir(self) -> Path:
        """مجلد السجلات"""
        return self.workspace_root / "logs"

    @property
    def data_dir(self) -> Path:
        """مجلد البيانات"""
        return self.workspace_root / "data"

    def initialize(self):
        """تهيئة مجلدات مساحة العمل"""
        dirs = [
            self.workspace_root,
            self.repos_dir,
            self.logs_dir,
            self.data_dir,
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            if not os.access(dir_path, os.W_OK):
                raise PermissionError(f"No write permission for {dir_path}")

    def get_repo_path(self, repo_id: str) -> Path:
        """الحصول على مسار مستودع محدد"""
        repo_path = self.repos_dir / repo_id
        repo_path.mkdir(parents=True, exist_ok=True)
        return repo_path

    def get_log_path(self, job_id: str) -> Path:
        """الحصول على مسار ملف سجل لمهمة"""
        return self.logs_dir / f"{job_id}.log"

    def repo_exists(self, repo_id: str) -> bool:
        """التحقق من وجود مجلد المستودع"""
        repo_path = self.repos_dir / repo_id
        return repo_path.exists() and repo_path.is_dir()

    def is_git_repo(self, repo_id: str) -> bool:
        """التحقق مما إذا كان المجلد يحتوي على مستودع Git"""
        repo_path = self.repos_dir / repo_id
        git_dir = repo_path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def delete_repo(self, repo_id: str) -> bool:
        """حذف مجلد مستودع بالكامل"""
        repo_path = self.repos_dir / repo_id
        if repo_path.exists():
            shutil.rmtree(repo_path)
            return True
        return False

    def get_disk_usage(self) -> dict:
        """الحصول على معلومات استخدام القرص"""
        total_size = 0
        file_count = 0

        for dir_path in [self.repos_dir, self.logs_dir, self.data_dir]:
            if dir_path.exists():
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = Path(root) / file
                        if file_path.exists():
                            total_size += file_path.stat().st_size
                            file_count += 1

        return {
            "workspace_root": str(self.workspace_root),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_files": file_count,
        }

    def cleanup_old_logs(self, days: int = 7):
        """تنظيف السجلات القديمة"""
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)
        log_files = list(self.logs_dir.glob("*.log"))

        cleaned = 0
        for log_file in log_files:
            if log_file.is_file():
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff:
                    log_file.unlink()
                    cleaned += 1

        return cleaned


# نسخة عالمية
workspace_service = WorkspaceService()
