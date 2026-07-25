from .health import router as health_router
from .version import router as version_router
from .repositories import router as repositories_router
from .jobs import router as jobs_router

def register_routes(app):
    """تسجيل جميع المسارات"""
    app.include_router(health_router)
    app.include_router(version_router)
    app.include_router(repositories_router)
    app.include_router(jobs_router)
