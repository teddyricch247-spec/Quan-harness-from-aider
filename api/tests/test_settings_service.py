import pytest
from pathlib import Path
import sys

# إضافة المجلد الرئيسي للمسار
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.database.database import db_service
from api.services.settings_service import settings_service

@pytest.fixture(autouse=True)
def setup_database():
    """تهيئة قاعدة البيانات قبل كل اختبار"""
    db_service.initialize()
    yield
    db_service.close()

def test_default_settings_exist():
    """التحقق من وجود الإعدادات الافتراضية"""
    assert settings_service.get("default_model") == "openai/gpt-4o-mini"
    assert settings_service.get("git_user_name") == "Aider Agent"
    assert settings_service.get("job_timeout_seconds") == 300

def test_set_and_get_string():
    """اختبار حفظ وقراءة قيمة نصية"""
    settings_service.set("test_key", "test_value")
    assert settings_service.get("test_key") == "test_value"

def test_set_and_get_integer():
    """اختبار حفظ وقراءة قيمة عددية"""
    settings_service.set("timeout", 120)
    assert settings_service.get("timeout") == 120
    assert isinstance(settings_service.get("timeout"), int)

def test_set_and_get_boolean():
    """اختبار حفظ وقراءة قيمة منطقية"""
    settings_service.set("debug", True)
    assert settings_service.get("debug") is True
    assert isinstance(settings_service.get("debug"), bool)

def test_set_and_get_json():
    """اختبار حفظ وقراءة JSON"""
    data = {"key": "value", "nested": [1, 2, 3]}
    settings_service.set("complex", data)
    result = settings_service.get("complex")
    assert result == data
    assert isinstance(result, dict)

def test_cache_consistency():
    """اختبار تناسق الذاكرة المؤقتة"""
    settings_service.set("cached_key", "initial")
    assert settings_service.get("cached_key") == "initial"
    
    # تحديث مباشر في قاعدة البيانات
    conn = db_service.get_connection()
    conn.execute("UPDATE settings SET value = 'direct_update' WHERE key = 'cached_key'")
    conn.commit()
    
    # الذاكرة المؤقتة لا تزال تحتوي على القيمة القديمة
    assert settings_service.get("cached_key") == "initial"
    
    # بعد إعادة التحميل تصبح مطابقة
    settings_service.reload_cache()
    assert settings_service.get("cached_key") == "direct_update"

def test_default_value():
    """اختبار القيمة الافتراضية للمفاتيح غير الموجودة"""
    assert settings_service.get("non_existent", "default") == "default"
    assert settings_service.get("non_existent") is None
