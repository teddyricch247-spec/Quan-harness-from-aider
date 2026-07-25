"""
Aider Agent API - المنصة الرئيسية
خدمة مستقلة لإدارة Aider كوكيل برمجي عبر HTTP
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# إضافة المجلد الرئيسي للمسار
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.database.database import db_service
from api.services.settings_service import settings_service
from api.services.workspace_service import workspace_service
from api.services.process_service import process_service
from api.routes import register_routes

# ============================================================
# إعداد التسجيل (stdout فقط في البداية)
# ============================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger("aider-agent")

# ============================================================
# إدارة دورة حياة التطبيق
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    دورة حياة التطبيق:
    1. workspace (مستقل)
    2. database
    3. settings (تعتمد على database)
    4. باقي الخدمات
    """

    # ========== بدء التشغيل ==========
    logger.info("=" * 60)
    logger.info("🚀 بدء تشغيل Aider Agent API")
    logger.info(f"⏰ الوقت: {datetime.utcnow().isoformat()}")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info("=" * 60)

    try:
        # 1. تهيئة مساحة العمل أولاً (لا تعتمد على أي خدمة)
        logger.info("📂 تهيئة مساحة العمل...")
        workspace_service.initialize()
        logger.info(f"   ✓ المجلدات جاهزة في: {workspace_service.workspace_root}")

        # 2. تهيئة قاعدة البيانات
        logger.info("🗄️ تهيئة قاعدة البيانات...")
        db_service.initialize()
        logger.info(f"   ✓ SQLite جاهز: {workspace_service.data_dir / 'agent.db'}")

        # 3. إضافة FileHandler الآن بعد أن أصبح workspace جاهزاً
        log_file = workspace_service.logs_dir / "api.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.getLogger().addHandler(file_handler)

        # 4. تحميل الإعدادات (بعد تهيئة قاعدة البيانات)
        logger.info("⚙️ تحميل الإعدادات...")
        model = settings_service.get_default_model()
        timeout = settings_service.get_job_timeout()
        logger.info(f"   ✓ النموذج الافتراضي: {model}")
        logger.info(f"   ✓ مهلة المهام: {timeout} ثانية")

        # 5. تعيين مهلة العمليات
        process_service.set_timeout(timeout)

        logger.info("✅ جميع الخدمات جاهزة للعمل")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ فشل تهيئة الخدمات: {e}", exc_info=True)
        raise

    yield

    # ========== إغلاق التطبيق ==========
    logger.info("=" * 60)
    logger.info("🛑 إيقاف تشغيل Aider Agent API")
    logger.info(f"⏰ الوقت: {datetime.utcnow().isoformat()}")

    try:
        active = process_service.get_active_processes()
        if active:
            logger.info(f"⚠️ يوجد {len(active)} عمليات نشطة، جاري إيقافها...")
            process_service.cleanup_all()
            logger.info("   ✓ تم إيقاف جميع العمليات")

        db_service.close()
        logger.info("   ✓ تم إغلاق قاعدة البيانات")

    except Exception as e:
        logger.error(f"❌ خطأ أثناء الإغلاق: {e}", exc_info=True)

    logger.info("✅ تم الإغلاق بأمان")
    logger.info("=" * 60)


# ============================================================
# إنشاء التطبيق
# ============================================================

app = FastAPI(
    title="Aider Agent API",
    description="""
## 🚀 منصة إدارة Aider كوكيل برمجي

### المميزات:
- 📂 **إدارة المستودعات**: استنساخ وتحديث وحذف مستودعات Git
- 🤖 **المهام الذكية**: تشغيل Aider مع نماذج مختلفة
- 📝 **السجلات**: تتبع كامل للمخرجات والأخطاء
- ⚙️ **الإعدادات**: تكوين مرن عبر API ومتغيرات البيئة

### المصادقة:
قم بتعيين `AGENT_API_TOKEN` في متغيرات البيئة لتفعيل المصادقة.
استخدم `Authorization: Bearer TOKEN` في رأس الطلب.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# ============================================================
# Middleware
# ============================================================

@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(os.urandom(8).hex()))
    start_time = datetime.utcnow()

    response = await call_next(request)

    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

    logger.info(
        f"{request.method} {request.url.path} | "
        f"Status: {response.status_code} | "
        f"Time: {process_time:.2f}ms | "
        f"ID: {request_id}"
    )

    return response


# ============================================================
# Exception Handlers
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"خطأ في المدخلات: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "البيانات المدخلة غير صالحة",
            "details": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"خطأ غير متوقع: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "حدث خطأ داخلي في الخادم",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ============================================================
# نقاط النهاية
# ============================================================

@app.get("/", tags=["root"])
def root():
    return {
        "service": "Aider Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat(),
    }

@app.get("/stats", tags=["monitoring"])
def get_stats():
    return {
        "disk_usage": workspace_service.get_disk_usage(),
        "active_processes": len(process_service.get_active_processes()),
        "active_processes_list": process_service.get_active_processes(),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================
# تسجيل المسارات
# ============================================================

register_routes(app)
logger.info("✅ تم تسجيل جميع المسارات")


# ============================================================
# نقطة التشغيل المباشر
# ============================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"🌐 تشغيل الخادم على {host}:{port}")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level=LOG_LEVEL.lower(),
        access_log=True,
        workers=1,
    )
