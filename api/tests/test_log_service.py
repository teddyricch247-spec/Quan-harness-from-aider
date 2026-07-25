import pytest
from pathlib import Path
import sys
import tempfile
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.log_service import log_service
from api.services.settings_service import settings_service
from api.services.workspace_service import WorkspaceService

@pytest.fixture
def temp_workspace_with_logs():
    """إنشاء مساحة عمل مع سجلات للاختبار"""
    with tempfile.TemporaryDirectory() as tmpdir:
        ws = WorkspaceService()
        settings_service.set("workspace_path", tmpdir)
        ws.initialize()
        
        # إنشاء سجل اختباري
        log_path = ws.get_log_path("test-job-1")
        log_content = """=== Process started at 2024-01-01T10:00:00 ===
Command: aider --message "Add tests"
Working dir: /workspace/repos/test

[2024-01-01T10:00:01] Starting Aider
[2024-01-01T10:00:05] Processing files...
[2024-01-01T10:00:10] Error: File not found
[2024-01-01T10:00:15] Warning: Model slow
[2024-01-01T10:00:20] Task completed
=== Process finished at 2024-01-01T10:00:25 ===
"""
        log_path.write_text(log_content)
        
        yield ws

def test_get_log(temp_workspace_with_logs):
    """اختبار قراءة السجل"""
    log_content = log_service.get_log("test-job-1")
    assert log_content is not None
    assert "Starting Aider" in log_content
    assert "Task completed" in log_content

def test_get_log_tail(temp_workspace_with_logs):
    """اختبار قراءة آخر السطور"""
    tail = log_service.get_log_tail("test-job-1", lines=3)
    assert tail is not None
    lines = tail.split("\n")
    assert len(lines) <= 3
    assert "Task completed" in lines[-1]

def test_get_log_since(temp_workspace_with_logs):
    """اختبار قراءة السجل منذ وقت محدد"""
    since = datetime(2024, 1, 1, 10, 0, 10)
    filtered = log_service.get_log_since("test-job-1", since)
    assert filtered is not None
    assert "Task completed" in filtered
    assert "Starting Aider" not in filtered  # قبل الوقت المحدد

def test_search_logs(temp_workspace_with_logs):
    """اختبار البحث في السجلات"""
    results = log_service.search_logs("test-job-1", "error")
    assert len(results) > 0
    assert "Error" in results[0]["content"]

def test_get_log_stats(temp_workspace_with_logs):
    """اختبار إحصائيات السجل"""
    stats = log_service.get_log_stats("test-job-1")
    assert stats is not None
    assert stats["total_lines"] > 0
    assert stats["error_lines"] >= 1
    assert stats["warning_lines"] >= 1
    assert stats["duration_seconds"] == 25.0  # 10:00:25 - 10:00:00

def test_get_all_job_ids(temp_workspace_with_logs):
    """اختبار الحصول على معرفات المهام"""
    # إنشاء سجل آخر
    ws = temp_workspace_with_logs
    (ws.get_log_path("test-job-2")).write_text("Another log")
    
    job_ids = log_service.get_all_job_ids()
    assert "test-job-1" in job_ids
    assert "test-job-2" in job_ids

def test_nonexistent_log():
    """اختبار سجل غير موجود"""
    assert log_service.get_log("non-existent") is None
    assert log_service.get_log_tail("non-existent") is None
    assert log_service.search_logs("non-existent", "test") == []

def test_format_for_display(temp_workspace_with_logs):
    """اختبار تنسيق العرض"""
    html = log_service.format_for_display("test-job-1", "html")
    assert html is not None
    assert "<pre>" in html
    assert '<span style="color:red">' in html
    
    json_format = log_service.format_for_display("test-job-1", "json")
    assert json_format is not None
    assert '"job_id"' in json_format
