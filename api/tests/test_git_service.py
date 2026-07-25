import pytest
from pathlib import Path
import sys
import tempfile
import subprocess

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.settings_service import settings_service
from api.services.workspace_service import WorkspaceService
from api.services.git_service import git_service

@pytest.fixture
def temp_git_repo():
    """إنشاء مستودع Git مؤقت للاختبار"""
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = WorkspaceService()
        settings_service.set("workspace_path", tmpdir)
        ws.initialize()
        
        # إنشاء مستودع اختباري
        repo_path = ws.get_repo_path("test-repo")
        subprocess.run(["git", "init"], cwd=str(repo_path), capture_output=True)
        
        # إضافة ملف أولي
        (repo_path / "README.md").write_text("# Test Repo")
        subprocess.run(["git", "add", "."], cwd=str(repo_path), capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo_path), capture_output=True)
        
        yield ws, repo_path

def test_get_current_branch(temp_git_repo):
    """اختبار الحصول على الفرع الحالي"""
    ws, repo_path = temp_git_repo
    branch = git_service.get_current_branch(repo_path)
    assert branch is not None
    assert len(branch) > 0

def test_get_last_commit(temp_git_repo):
    """اختبار الحصول على آخر التزام"""
    ws, repo_path = temp_git_repo
    commit = git_service.get_last_commit(repo_path)
    assert commit is not None
    assert len(commit) == 7  # SHA مختصر

def test_get_status(temp_git_repo):
    """اختبار حالة المستودع"""
    ws, repo_path = temp_git_repo
    
    # المستودع نظيف
    status = git_service.get_status(repo_path)
    assert status["is_clean"]
    
    # إضافة تغيير
    (repo_path / "new_file.txt").write_text("new content")
    status = git_service.get_status(repo_path)
    assert not status["is_clean"]
    assert len(status["files_untracked"]) > 0

def test_stage_and_commit(temp_git_repo):
    """اختبار التجهيز والالتزام"""
    ws, repo_path = temp_git_repo
    
    # إنشاء ملف جديد
    (repo_path / "test.txt").write_text("test")
    
    # تجهيز الملفات
    assert git_service.stage_all(repo_path)
    
    # إنشاء التزام
    success, output = git_service.commit(repo_path, "Test commit")
    assert success
    
    # التحقق من نظافة المستودع بعد الالتزام
    status = git_service.get_status(repo_path)
    assert status["is_clean"]

def test_configure_identity(temp_git_repo):
    """اختبار تكوين الهوية"""
    ws, repo_path = temp_git_repo
    
    git_service.configure_identity(repo_path, "Test User", "test@test.com")
    
    # التحقق من الإعدادات
    import subprocess
    name = subprocess.run(
        ["git", "config", "user.name"], 
        cwd=str(repo_path), 
        capture_output=True, 
        text=True
    )
    assert "Test User" in name.stdout

def test_is_repo_ready(temp_git_repo):
    """اختبار جاهزية المستودع"""
    ws, repo_path = temp_git_repo
    assert git_service.is_repo_ready(repo_path)
    
    # مجلد غير موجود
    fake_path = ws.repos_dir / "non-existent"
    assert not git_service.is_repo_ready(fake_path)
