import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from .settings_service import settings_service
from .workspace_service import workspace_service

class GitService:
    def __init__(self):
        self._git_path = "git"

    def _run_git(self, repo_path: Path, *args, timeout: int = 30) -> Tuple[int, str, str]:
        """تشغيل أمر Git في مسار محدد"""
        command = [self._git_path] + list(args)
        
        result = subprocess.run(
            command,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def clone(self, url: str, repo_path: Path, branch: Optional[str] = None) -> bool:
        """استنساخ مستودع"""
        if not repo_path.exists():
            repo_path.mkdir(parents=True, exist_ok=True)

        # إذا كان المجلد غير فارغ، نتحقق أولاً
        if any(repo_path.iterdir()):
            return self._update_existing(repo_path, url, branch)

        args = ["clone", url, str(repo_path)]
        if branch:
            args.extend(["-b", branch])
        
        returncode, stdout, stderr = self._run_git(repo_path.parent, *args, timeout=120)
        return returncode == 0

    def _update_existing(self, repo_path: Path, url: str, branch: Optional[str] = None) -> bool:
        """تحديث مستودع موجود"""
        # التحقق من أنه مستودع Git
        if not (repo_path / ".git").exists():
            return False

        # جلب التحديثات
        returncode, _, stderr = self._run_git(repo_path, "fetch", "origin", timeout=60)
        if returncode != 0:
            return False

        # التبديل إلى الفرع المطلوب
        if branch:
            self._run_git(repo_path, "checkout", branch)

        # دمج التغييرات
        target = branch or "main"
        returncode, _, stderr = self._run_git(
            repo_path, "reset", "--hard", f"origin/{target}", timeout=30
        )
        return returncode == 0

    def pull(self, repo_path: Path, branch: Optional[str] = None) -> bool:
        """سحب آخر التحديثات"""
        if branch:
            self._run_git(repo_path, "checkout", branch, timeout=15)
        
        returncode, stdout, stderr = self._run_git(repo_path, "pull", "origin", timeout=60)
        return returncode == 0

    def get_current_branch(self, repo_path: Path) -> Optional[str]:
        """الحصول على الفرع الحالي"""
        returncode, stdout, stderr = self._run_git(
            repo_path, "rev-parse", "--abbrev-ref", "HEAD", timeout=5
        )
        if returncode == 0:
            return stdout
        return None

    def get_last_commit(self, repo_path: Path, short: bool = True) -> Optional[str]:
        """الحصول على آخر التزام"""
        args = ["log", "-1"]
        if short:
            args.append("--pretty=format:%h")
        else:
            args.append("--pretty=format:%H")
        
        returncode, stdout, stderr = self._run_git(repo_path, *args, timeout=5)
        if returncode == 0:
            return stdout
        return None

    def get_status(self, repo_path: Path) -> dict:
        """الحصول على حالة المستودع"""
        returncode, stdout, stderr = self._run_git(repo_path, "status", "--porcelain", timeout=5)
        
        files_modified = []
        files_untracked = []
        
        if returncode == 0 and stdout:
            for line in stdout.split("\n"):
                if line.strip():
                    status = line[:2]
                    filename = line[3:]
                    if status.strip() == "??":
                        files_untracked.append(filename)
                    else:
                        files_modified.append({"status": status, "file": filename})
        
        return {
            "branch": self.get_current_branch(repo_path),
            "last_commit": self.get_last_commit(repo_path),
            "files_modified": files_modified,
            "files_untracked": files_untracked,
            "is_clean": len(files_modified) == 0 and len(files_untracked) == 0
        }

    def configure_identity(self, repo_path: Path, name: Optional[str] = None, email: Optional[str] = None):
        """تكوين هوية Git للمستودع"""
        if not name or not email:
            name, email = settings_service.get_git_identity()
        
        self._run_git(repo_path, "config", "user.name", name, timeout=5)
        self._run_git(repo_path, "config", "user.email", email, timeout=5)

    def is_repo_ready(self, repo_path: Path) -> bool:
        """التحقق من أن المستودع جاهز للعمل"""
        checks = [
            repo_path.exists(),
            (repo_path / ".git").exists(),
            self.get_current_branch(repo_path) is not None
        ]
        return all(checks)

    def stage_all(self, repo_path: Path) -> bool:
        """إضافة جميع التغييرات إلى منطقة التجهيز"""
        returncode, _, _ = self._run_git(repo_path, "add", ".", timeout=10)
        return returncode == 0

    def commit(self, repo_path: Path, message: str) -> Tuple[bool, str]:
        """إنشاء التزام جديد"""
        returncode, stdout, stderr = self._run_git(
            repo_path, "commit", "-m", message, timeout=10
        )
        success = returncode == 0
        output = stdout if success else stderr
        return success, output

    def push(self, repo_path: Path, branch: Optional[str] = None) -> bool:
        """دفع التغييرات إلى المستودع البعيد"""
        args = ["push"]
        if branch:
            args.extend(["origin", branch])
        
        returncode, _, _ = self._run_git(repo_path, *args, timeout=60)
        return returncode == 0

# نسخة عالمية
git_service = GitService()
