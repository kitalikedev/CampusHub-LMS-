"""Tạo ứng dụng FastAPI. Thêm module mới: thêm một dòng vào ROUTERS (06 §4.4)."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.models  # noqa: F401  nạp đủ model trước khi dùng relationship
from src.core.config import settings
from src.core.errors import register_error_handlers
from src.modules.academics.router import router as academics_router
from src.modules.announcements.router import router as announcements_router
from src.modules.assignments.router import router as assignments_router
from src.modules.audit.router import router as audit_router
from src.modules.auth.router import router as auth_router
from src.modules.enrollments.router import router as enrollments_router
from src.modules.grading.router import router as grading_router
from src.modules.notifications.router import router as notifications_router
from src.modules.regrades.router import router as regrades_router
from src.modules.rooms.router import router as rooms_router
from src.modules.sections.router import router as sections_router
from src.modules.stats.router import router as stats_router
from src.modules.submissions.router import router as submissions_router
from src.modules.transcripts.router import router as transcripts_router
from src.modules.users.router import router as users_router

ROUTERS = [
    auth_router, users_router, academics_router, rooms_router, sections_router, enrollments_router,
    assignments_router, submissions_router, grading_router, transcripts_router, regrades_router,
    announcements_router, notifications_router, audit_router, stats_router,
]


def create_app() -> FastAPI:
    app = FastAPI(title="CampusHub v3 API", version="3.0.0")
    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=False,
                       allow_methods=["*"], allow_headers=["*"])  # NFR-SEC-05
    register_error_handlers(app)
    for router in ROUTERS:
        app.include_router(router, prefix="/api")

    @app.get("/api/health", tags=["health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
