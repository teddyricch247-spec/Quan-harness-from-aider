import os
import sqlite3
from pathlib import Path
from datetime import datetime

# المسارات
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "/workspace"))
DATA_DIR = WORKSPACE_DIR / "data"
LOGS_DIR = WORKSPACE_DIR / "logs"
REPOS_DIR = WORKSPACE_DIR / "repos"
DB_PATH = DATA_DIR / "agent.db"

# الثوابت
JOB_STATUSES = ["pending", "running", "completed", "failed", "cancelled", "interrupted"]
REPO_STATUSES = ["pending", "cloning", "ready", "failed"]

class DatabaseService:
    def __init__(self):
        self._conn = None

    def initialize(self):
        """تهيئة قاعدة البيانات والمجلدات"""
        # إنشاء المجلدات
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        REPOS_DIR.mkdir(parents=True, exist_ok=True)

        # فتح اتصال SQLite
        self._conn = sqlite3.connect(str(DB_PATH))
        self._conn.row_factory = sqlite3.Row

        # تفعيل الإعدادات الأساسية
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._conn.execute("PRAGMA journal_mode = WAL;")
        self._conn.execute("PRAGMA synchronous = NORMAL;")

        # تنفيذ المخطط
        schema_path = Path(__file__).parent / "schema.sql"
        schema_sql = schema_path.read_text(encoding="utf-8")
        self._conn.executescript(schema_sql)
        self._conn.commit()

        # استعادة الحالة: تحويل running إلى interrupted
        self._recover_interrupted_jobs()

        # إدراج الإعدادات الافتراضية
        self._insert_default_settings()

    def _recover_interrupted_jobs(self):
        """تحويل المهام قيد التشغيل إلى متوقفة"""
        cursor = self._conn.execute("SELECT id FROM jobs WHERE status = 'running'")
        interrupted_jobs = cursor.fetchall()

        for row in interrupted_jobs:
            job_id = row["id"]
            self._conn.execute(
                "UPDATE jobs SET status = 'interrupted', error_message = ?, updated_at = ? WHERE id = ?",
                ("Service restarted before job completion", datetime.utcnow().isoformat(), job_id)
            )
            self._conn.execute(
                "INSERT INTO job_events (job_id, event, details) VALUES (?, 'interrupted', ?)",
                (job_id, "Service restarted before job completion")
            )
        if interrupted_jobs:
            self._conn.commit()

    def _insert_default_settings(self):
        """إدراج الإعدادات الافتراضية إذا لم تكن موجودة"""
        defaults = {
            "default_model": "openai/gpt-4o-mini",
            "workspace_path": str(WORKSPACE_DIR),
            "git_user_name": "Aider Agent",
            "git_user_email": "agent@aider.local",
            "job_timeout_seconds": "300"
        }
        for key, value in defaults.items():
            self._conn.execute(
                "INSERT OR IGNORE INTO settings (key, value, type) VALUES (?, ?, 'string')",
                (key, value)
            )
        self._conn.commit()

    def get_connection(self):
        """الحصول على اتصال قاعدة البيانات"""
        if not self._conn:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._conn

    def close(self):
        """إغلاق اتصال قاعدة البيانات"""
        if self._conn:
            self._conn.close()
            self._conn = None

# نسخة عالمية للاستخدام في الخدمات
db_service = DatabaseService()
