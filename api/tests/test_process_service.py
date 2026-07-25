import pytest
from pathlib import Path
import sys
import tempfile
import time
import platform

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.process_service import process_service

@pytest.fixture
def temp_workspace():
    """إنشاء مجلد مؤقت للاختبار"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

def test_start_and_check_process(temp_workspace):
    """اختبار بدء عملية والتحقق من حالتها"""
    log_path = temp_workspace / "test.log"
    
    # بدء عملية بسيطة
    info = process_service.start_process(
        command=["python", "-c", "import time; time.sleep(0.5); print('done')"],
        cwd=temp_workspace,
        job_id="test-job-1",
        log_path=log_path
    )
    
    assert info.pid is not None
    assert info.status == "running"
    
    # انتظار انتهاء العملية
    time.sleep(1)
    
    finished, returncode = process_service.check_process(info.process_id)
    assert finished
    assert returncode == 0
    
    # التحقق من كتابة السجل
    assert log_path.exists()
    log_content = log_path.read_text()
    assert "done" in log_content

def test_stop_process(temp_workspace):
    """اختبار إيقاف عملية"""
    log_path = temp_workspace / "test_stop.log"
    
    # بدء عملية طويلة
    info = process_service.start_process(
        command=["python", "-c", "import time; time.sleep(30)"],
        cwd=temp_workspace,
        job_id="test-job-2",
        log_path=log_path
    )
    
    # إيقاف العملية
    result = process_service.stop_process(info.process_id)
    assert result
    
    # التحقق من توقف العملية
    finished, _ = process_service.check_process(info.process_id)
    assert finished

def test_get_process_by_job(temp_workspace):
    """اختبار البحث عن عملية بواسطة معرف المهمة"""
    log_path = temp_workspace / "test_job.log"
    
    info = process_service.start_process(
        command=["python", "-c", "import time; time.sleep(1)"],
        cwd=temp_workspace,
        job_id="specific-job",
        log_path=log_path
    )
    
    found = process_service.get_process_by_job("specific-job")
    assert found is not None
    assert found.job_id == "specific-job"
    
    not_found = process_service.get_process_by_job("non-existent")
    assert not_found is None

def test_cleanup_process(temp_workspace):
    """اختبار تنظيف العملية"""
    log_path = temp_workspace / "test_cleanup.log"
    
    info = process_service.start_process(
        command=["python", "-c", "print('hello')"],
        cwd=temp_workspace,
        job_id="test-cleanup",
        log_path=log_path
    )
    
    # انتظار الانتهاء
    time.sleep(0.5)
    
    process_id = info.process_id
    process_service.cleanup_process(process_id)
    
    # التأكد من حذف العملية
    assert process_service.get_process(process_id) is None

def test_active_processes(temp_workspace):
    """اختبار قائمة العمليات النشطة"""
    log_path = temp_workspace / "test_active.log"
    
    # بدء عدة عمليات
    info1 = process_service.start_process(
        command=["python", "-c", "import time; time.sleep(2)"],
        cwd=temp_workspace,
        job_id="active-1",
        log_path=log_path
    )
    
    active = process_service.get_active_processes()
    assert len(active) >= 1
    
    # تنظيف
    process_service.stop_process(info1.process_id, force=True)

@pytest.mark.skipif(platform.system() != "Linux", reason="preexec_fn for Linux only")
def test_process_group_isolation():
    """اختبار عزل مجموعة العمليات (Linux فقط)"""
    # هذا الاختبار خاص بـ Linux بسبب preexec_fn
    pass
