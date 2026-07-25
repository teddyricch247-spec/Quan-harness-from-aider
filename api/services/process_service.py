import os
import signal
import subprocess
import uuid
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
from .settings_service import settings_service

class ProcessInfo:
    """معلومات عملية قيد التشغيل"""
    def __init__(self, process_id: str, pid: int, process: subprocess.Popen, 
                 job_id: str, log_path: Path):
        self.process_id = process_id
        self.pid = pid
        self.process = process
        self.job_id = job_id
        self.log_path = log_path
        self.started_at = datetime.utcnow()
        self.status = "running"

class ProcessService:
    def __init__(self):
        self._processes: Dict[str, ProcessInfo] = {}
        self._timeout = 300  # ثواني افتراضية

    def start_process(self, 
                     command: list, 
                     cwd: Path, 
                     job_id: str,
                     log_path: Path) -> ProcessInfo:
        """بدء عملية جديدة"""
        process_id = str(uuid.uuid4())
        
        # فتح ملف السجل
        log_file = open(log_path, "w", encoding="utf-8")
        log_file.write(f"=== Process started at {datetime.utcnow().isoformat()} ===\n")
        log_file.write(f"Command: {' '.join(command)}\n")
        log_file.write(f"Working dir: {cwd}\n\n")
        log_file.flush()

        try:
            # بدء العملية كمجموعة منفصلة للتحكم بها بسهولة
            process = subprocess.Popen(
                command,
                cwd=str(cwd),
                stdout=log_file,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid  # Linux فقط
            )
        except Exception as e:
            log_file.write(f"\n=== Process failed to start: {e} ===\n")
            log_file.close()
            raise

        # حفظ معلومات العملية
        info = ProcessInfo(
            process_id=process_id,
            pid=process.pid,
            process=process,
            job_id=job_id,
            log_path=log_path
        )
        
        self._processes[process_id] = info
        return info

    def get_process(self, process_id: str) -> Optional[ProcessInfo]:
        """الحصول على معلومات عملية"""
        return self._processes.get(process_id)

    def get_process_by_job(self, job_id: str) -> Optional[ProcessInfo]:
        """البحث عن عملية بواسطة معرف المهمة"""
        for info in self._processes.values():
            if info.job_id == job_id:
                return info
        return None

    def check_process(self, process_id: str) -> Tuple[bool, Optional[int]]:
        """التحقق من حالة العملية"""
        info = self._processes.get(process_id)
        if not info:
            return False, None

        returncode = info.process.poll()
        
        if returncode is not None:
            # انتهت العملية
            info.status = "completed" if returncode == 0 else "failed"
            # إغلاق ملف السجل
            if not info.process.stdout.closed:
                info.process.stdout.close()
            return True, returncode
        
        # ما زالت قيد التشغيل
        return False, None

    def stop_process(self, process_id: str, force: bool = False) -> bool:
        """إيقاف عملية"""
        info = self._processes.get(process_id)
        if not info:
            return False

        # التحقق مما إذا كانت العملية ما زالت قيد التشغيل
        if info.process.poll() is not None:
            info.status = "already_stopped"
            return True

        try:
            if force:
                # إيقاف قسري
                os.killpg(os.getpgid(info.process.pid), signal.SIGKILL)
            else:
                # إيقاف لطيف
                os.killpg(os.getpgid(info.process.pid), signal.SIGTERM)
            
            # انتظار انتهاء العملية
            try:
                info.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if not force:
                    # إذا لم يستجب SIGTERM، نجبره
                    os.killpg(os.getpgid(info.process.pid), signal.SIGKILL)
                    info.process.wait(timeout=2)
            
            info.status = "stopped"
            
            # إغلاق ملف السجل
            if not info.process.stdout.closed:
                log_file = open(info.log_path, "a", encoding="utf-8")
                log_file.write(f"\n=== Process stopped at {datetime.utcnow().isoformat()} ===\n")
                log_file.close()
                info.process.stdout.close()
            
            return True
            
        except Exception as e:
            info.status = f"stop_failed: {e}"
            return False

    def cleanup_process(self, process_id: str):
        """تنظيف معلومات العملية من الذاكرة"""
        info = self._processes.get(process_id)
        if info:
            # التأكد من إغلاق الملفات
            if info.process.stdout and not info.process.stdout.closed:
                info.process.stdout.close()
            # حذف من القاموس
            del self._processes[process_id]

    def get_active_processes(self) -> list:
        """الحصول على قائمة العمليات النشطة"""
        active = []
        for pid, info in self._processes.items():
            if info.process.poll() is None:
                active.append({
                    "process_id": pid,
                    "pid": info.pid,
                    "job_id": info.job_id,
                    "started_at": info.started_at.isoformat()
                })
        return active

    def cleanup_all(self):
        """تنظيف جميع العمليات (عند إغلاق الخدمة)"""
        for pid in list(self._processes.keys()):
            info = self._processes[pid]
            if info.process.poll() is None:
                self.stop_process(pid, force=True)
            self.cleanup_process(pid)

    def set_timeout(self, seconds: int):
        """تعيين مهلة العمليات"""
        self._timeout = seconds

    def get_timeout(self) -> int:
        """الحصول على مهلة العمليات"""
        return self._timeout

# نسخة عالمية
process_service = ProcessService()
