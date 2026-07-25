from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import re
from .workspace_service import workspace_service

class LogService:
    def __init__(self):
        self._max_log_age_days = 30

    def get_log(self, job_id: str) -> Optional[str]:
        """قراءة سجل مهمة كامل"""
        log_path = workspace_service.get_log_path(job_id)
        
        if not log_path.exists():
            return None
        
        try:
            return log_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

    def get_log_tail(self, job_id: str, lines: int = 50) -> Optional[str]:
        """قراءة آخر سطور من السجل"""
        log_content = self.get_log(job_id)
        if not log_content:
            return None
        
        all_lines = log_content.split("\n")
        last_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        return "\n".join(last_lines)

    def get_log_since(self, job_id: str, since: datetime) -> Optional[str]:
        """قراءة السجل منذ وقت محدد"""
        log_content = self.get_log(job_id)
        if not log_content:
            return None
        
        # استخراج السطور التي تحتوي على طوابع زمنية بعد 'since'
        filtered_lines = []
        for line in log_content.split("\n"):
            timestamp = self._extract_timestamp(line)
            if timestamp and timestamp >= since:
                filtered_lines.append(line)
        
        return "\n".join(filtered_lines)

    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """محاولة استخراج طابع زمني من سطر سجل"""
        # تنسيقات شائعة
        patterns = [
            (r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '%Y-%m-%dT%H:%M:%S'),
            (r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '%Y-%m-%d %H:%M:%S'),
            (r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', '[%Y-%m-%d %H:%M:%S]'),
        ]
        
        for pattern, date_format in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(0)
                    # إزالة الأقواس إن وجدت
                    timestamp_str = timestamp_str.strip('[]')
                    return datetime.strptime(timestamp_str, date_format)
                except ValueError:
                    continue
        
        return None

    def search_logs(self, job_id: str, query: str, context_lines: int = 2) -> List[Dict]:
        """البحث في السجلات مع سياق"""
        log_content = self.get_log(job_id)
        if not log_content:
            return []
        
        all_lines = log_content.split("\n")
        results = []
        
        for i, line in enumerate(all_lines):
            if query.lower() in line.lower():
                # جمع السياق
                start = max(0, i - context_lines)
                end = min(len(all_lines), i + context_lines + 1)
                
                context = []
                for j in range(start, end):
                    context.append({
                        "line_number": j + 1,
                        "content": all_lines[j],
                        "is_match": j == i
                    })
                
                results.append({
                    "match_line": i + 1,
                    "content": line,
                    "context": context
                })
        
        return results

    def get_log_stats(self, job_id: str) -> Optional[Dict]:
        """الحصول على إحصائيات السجل"""
        log_content = self.get_log(job_id)
        if not log_content:
            return None
        
        lines = log_content.split("\n")
        total_lines = len(lines)
        total_chars = len(log_content)
        
        # إحصائيات إضافية
        error_lines = sum(1 for line in lines if "error" in line.lower())
        warning_lines = sum(1 for line in lines if "warning" in line.lower())
        
        # العثور على أول وآخر طابع زمني
        first_timestamp = None
        last_timestamp = None
        
        for line in lines:
            ts = self._extract_timestamp(line)
            if ts:
                if not first_timestamp:
                    first_timestamp = ts
                last_timestamp = ts
        
        duration = None
        if first_timestamp and last_timestamp:
            duration = (last_timestamp - first_timestamp).total_seconds()
        
        return {
            "job_id": job_id,
            "total_lines": total_lines,
            "total_chars": total_chars,
            "error_lines": error_lines,
            "warning_lines": warning_lines,
            "first_timestamp": first_timestamp.isoformat() if first_timestamp else None,
            "last_timestamp": last_timestamp.isoformat() if last_timestamp else None,
            "duration_seconds": duration
        }

    def cleanup_old_logs(self, days: int = None) -> int:
        """تنظيف السجلات القديمة"""
        if days is None:
            days = self._max_log_age_days
        
        return workspace_service.cleanup_old_logs(days)

    def get_all_job_ids(self) -> List[str]:
        """الحصول على قائمة بمعرفات المهام من ملفات السجل"""
        log_files = list(workspace_service.logs_dir.glob("*.log"))
        job_ids = []
        
        for log_file in log_files:
            job_id = log_file.stem  # اسم الملف بدون الامتداد
            job_ids.append(job_id)
        
        return sorted(job_ids)

    def stream_log(self, job_id: str):
        """مولد لبث السجل سطراً سطراً"""
        log_path = workspace_service.get_log_path(job_id)
        
        if not log_path.exists():
            yield "Log file not found"
            return
        
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            while True:
                line = f.readline()
                if line:
                    yield line
                else:
                    # انتظار كتابة المزيد من السطور
                    import time
                    time.sleep(0.1)

    def format_for_display(self, job_id: str, format_type: str = "text") -> Optional[str]:
        """تنسيق السجل للعرض"""
        log_content = self.get_log(job_id)
        if not log_content:
            return None
        
        if format_type == "html":
            # تنسيق HTML بسيط
            formatted = log_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            formatted = formatted.replace("\n", "<br>\n")
            # تلوين الأخطاء
            formatted = formatted.replace("error", '<span style="color:red">error</span>')
            formatted = formatted.replace("ERROR", '<span style="color:red">ERROR</span>')
            formatted = formatted.replace("warning", '<span style="color:orange">warning</span>')
            return f"<pre>{formatted}</pre>"
        
        elif format_type == "json":
            # تنسيق JSON مع البيانات الوصفية
            import json
            stats = self.get_log_stats(job_id)
            return json.dumps({
                "job_id": job_id,
                "stats": stats,
                "content": log_content
            }, indent=2)
        
        else:  # text
            return log_content

# نسخة عالمية
log_service = LogService()
