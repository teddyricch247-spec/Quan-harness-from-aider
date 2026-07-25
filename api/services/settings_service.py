from typing import Any, Optional, Dict
from datetime import datetime
import json
from ..database.database import db_service

class SettingsService:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_loaded = False

    def _load_cache(self):
        """تحميل جميع الإعدادات في الذاكرة المؤقتة"""
        if self._cache_loaded:
            return
        
        conn = db_service.get_connection()
        cursor = conn.execute("SELECT key, value, type FROM settings")
        for row in cursor:
            self._cache[row["key"]] = self._convert_value(row["value"], row["type"])
        self._cache_loaded = True

    def _convert_value(self, value: str, type_name: str) -> Any:
        """تحويل القيمة النصية إلى النوع المناسب"""
        if type_name == "integer":
            return int(value)
        elif type_name == "boolean":
            return value.lower() in ("true", "1", "yes")
        elif type_name == "json":
            return json.loads(value)
        else:  # string
            return value

    def _serialize_value(self, value: Any) -> tuple:
        """تحديد نوع القيمة وتحويلها إلى نص"""
        if isinstance(value, bool):
            return str(value).lower(), "boolean"
        elif isinstance(value, int):
            return str(value), "integer"
        elif isinstance(value, (dict, list)):
            return json.dumps(value), "json"
        else:
            return str(value), "string"

    def get(self, key: str, default: Any = None) -> Any:
        """قراءة إعداد"""
        self._load_cache()
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """حفظ إعداد"""
        self._load_cache()
        serialized_value, type_name = self._serialize_value(value)
        
        conn = db_service.get_connection()
        conn.execute(
            """INSERT INTO settings (key, value, type, updated_at) 
               VALUES (?, ?, ?, ?)
               ON CONFLICT(key) DO UPDATE SET 
               value = excluded.value,
               type = excluded.type,
               updated_at = excluded.updated_at""",
            (key, serialized_value, type_name, datetime.utcnow().isoformat())
        )
        conn.commit()
        
        # تحديث الذاكرة المؤقتة
        self._cache[key] = value

    def get_all(self) -> Dict[str, Any]:
        """قراءة جميع الإعدادات"""
        self._load_cache()
        return self._cache.copy()

    def get_default_model(self) -> str:
        return self.get("default_model", "openai/gpt-4o-mini")

    def get_workspace_path(self) -> str:
        return self.get("workspace_path", "/workspace")

    def get_git_identity(self) -> tuple:
        return (
            self.get("git_user_name", "Aider Agent"),
            self.get("git_user_email", "agent@aider.local")
        )

    def get_job_timeout(self) -> int:
        return self.get("job_timeout_seconds", 300)

    def reload_cache(self):
        """إعادة تحميل الذاكرة المؤقتة (للاستخدام بعد التحديثات المباشرة)"""
        self._cache.clear()
        self._cache_loaded = False
        self._load_cache()

# نسخة عالمية
settings_service = SettingsService()
