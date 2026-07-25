import pytest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.settings_service import settings_service
from api.services.workspace_service import WorkspaceService

@pytest.fixture
def temp_workspace():
    """إنشاء مساحة عمل مؤقتة للاختبار"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # ضبط مسار workspace مؤقت
        settings_service.set("workspace_path", tmpdir)
        ws = WorkspaceService()
        ws.initialize()
        yield ws

def test_initialize_creates_directories(temp_workspace):
    """اختبار إنشاء المجلدات الأساسية"""
    ws = temp_workspace
    assert ws.workspace_root.exists()
    assert ws.repos_dir.exists()
    assert ws.logs_dir.exists()
    assert ws.data_dir.exists()

def test_get_repo_path(temp_workspace):
    """اختبار الحصول على مسار مستودع"""
    ws = temp_workspace
    repo_path = ws.get_repo_path("test-repo")
    assert repo_path.exists()
    assert repo_path.name == "test-repo"

def test_get_log_path(temp_workspace):
    """اختبار الحصول على مسار ملف سجل"""
    ws = temp_workspace
    log_path = ws.get_log_path("job-123")
    expected = ws.logs_dir / "job-123.log"
    assert log_path == expected

def test_repo_exists(temp_workspace):
    """اختبار التحقق من وجود مستودع"""
    ws = temp_workspace
    repo_path = ws.get_repo_path("my-repo")
    
    # قبل إنشاء الملفات
    assert ws.repo_exists("my-repo")
    assert not ws.is_git_repo("my-repo")
    
    # إنشاء مجلد .git وهمي
    (repo_path / ".git").mkdir()
    assert ws.is_git_repo("my-repo")

def test_delete_repo(temp_workspace):
    """اختبار حذف مستودع"""
    ws = temp_workspace
    ws.get_repo_path("to-delete")
    assert ws.repo_exists("to-delete")
    
    ws.delete_repo("to-delete")
    assert not ws.repo_exists("to-delete")

def test_disk_usage(temp_workspace):
    """اختبار معلومات استخدام القرص"""
    ws = temp_workspace
    
    # إنشاء ملف وهمي
    test_file = ws.repos_dir / "test.txt"
    test_file.write_text("test content")
    
    usage = ws.get_disk_usage()
    assert usage["total_size_bytes"] > 0
    assert usage["total_files"] >= 1
    assert "workspace_root" in usage
