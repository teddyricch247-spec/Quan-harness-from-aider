import pytest
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.aider_service import aider_service
from api.services.settings_service import settings_service
from api.services.workspace_service import WorkspaceService

@pytest.fixture
def temp_repo():
    """إنشاء مستودع وهمي للاختبار"""
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = WorkspaceService()
        settings_service.set("workspace_path", tmpdir)
        ws.initialize()
        
        repo_path = ws.get_repo_path("test-aider-repo")
        
        # جعله مستودع Git
        import subprocess
        subprocess.run(["git", "init"], cwd=str(repo_path), capture_output=True)
        (repo_path / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=str(repo_path), capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=str(repo_path), capture_output=True)
        
        yield repo_path

def test_build_command_basic(temp_repo):
    """اختبار بناء أمر أساسي"""
    command = aider_service.build_command(
        message="Add comment to function",
        repo_path=temp_repo
    )
    
    assert "aider" in command
    assert "--message" in command
    assert "Add comment to function" in command
    assert "--yes-always" in command
    assert "--no-pretty" in command

def test_build_command_with_files(temp_repo):
    """اختبار بناء أمر مع ملفات محددة"""
    command = aider_service.build_command(
        message="Refactor this file",
        repo_path=temp_repo,
        files=["main.py", "utils.py"]
    )
    
    assert "--file" in command
    assert "main.py" in command
    assert "utils.py" in command

def test_build_command_no_auto_commit(temp_repo):
    """اختبار بناء أمر بدون التزام تلقائي"""
    command = aider_service.build_command(
        message="Suggest changes",
        repo_path=temp_repo,
        auto_commits=False
    )
    
    assert "--yes" in command
    assert "--yes-always" not in command

def test_validate_model():
    """اختبار التحقق من صحة النموذج"""
    assert aider_service.validate_model("openai/gpt-4")
    assert aider_service.validate_model("anthropic/claude-3")
    assert aider_service.validate_model("ollama/llama2")
    
    assert not aider_service.validate_model("invalid-model")
    assert not aider_service.validate_model("gpt-4")

def test_estimate_tokens():
    """اختبار تقدير عدد الرموز"""
    message = "Hello, this is a test message with multiple words"
    tokens = aider_service.estimate_tokens(message)
    assert tokens > 0
    assert tokens < len(message)  # الرموز أقل من عدد الأحرف

def test_get_version():
    """اختبار الحصول على الإصدار"""
    version = aider_service.get_version()
    assert version is not None
    assert len(version) > 0
