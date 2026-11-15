"""Lỗi nghiệp vụ và định dạng lỗi chung (06 §2.5, danh mục 03 §8)."""
import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("campushub")

STATUS_BY_CODE: Dict[str, int] = {
    "AUTH_REQUIRED": 401,
    "AUTH_INVALID_CREDENTIALS": 401,
    "ACCOUNT_DISABLED": 403,
    "PASSWORD_CHANGE_REQUIRED": 403,
    "PASSWORD_POLICY_VIOLATION": 422,
    "CURRENT_PASSWORD_INCORRECT": 422,
    "FORBIDDEN": 403,
    "NOT_SECTION_INSTRUCTOR": 403,
    "NOT_ENROLLED": 403,
    "NOT_FOUND": 404,
    "VALIDATION_ERROR": 422,
    "IMPORT_INVALID_ROWS": 422,
    "PREREQUISITE_CYCLE": 422,
    "INVALID_TIME_RANGE": 422,
    "SUBMISSION_EMPTY": 422,
    "FILE_TYPE_NOT_ALLOWED": 422,
    "FILE_TOO_LARGE": 422,
    "GRADE_OUT_OF_RANGE": 422,
    "UNLOCK_REASON_REQUIRED": 422,
    "REGRADE_REASON_REQUIRED": 422,
    "INTERNAL_ERROR": 500,
}


class AppError(Exception):
    """Lỗi nghiệp vụ có mã. Mặc định HTTP 409 (vi phạm rule)."""

    def __init__(self, code: str, params: Optional[Dict[str, Any]] = None,
                 message: Optional[str] = None, status: Optional[int] = None) -> None:
        super().__init__(message or code)
        self.code = code
        self.params = params or {}
        self.message = message or code
        self.status = status or STATUS_BY_CODE.get(code, 409)


def error_body(code: str, message: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"error": {"code": code, "message": message, "params": params or {}}}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_req: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status, content=error_body(exc.code, exc.message, exc.params))

    @app.exception_handler(RequestValidationError)
    async def _validation(_req: Request, exc: RequestValidationError) -> JSONResponse:
        fields = [
            {"loc": ".".join(str(p) for p in err.get("loc", []) if p != "body"), "msg": err.get("msg", "")}
            for err in exc.errors()
        ]
        return JSONResponse(status_code=422,
                            content=error_body("VALIDATION_ERROR", "Dữ liệu không hợp lệ", {"fields": fields}))

    @app.exception_handler(StarletteHTTPException)
    async def _http(_req: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {401: "AUTH_REQUIRED", 403: "FORBIDDEN", 404: "NOT_FOUND"}.get(exc.status_code, "HTTP_ERROR")
        return JSONResponse(status_code=exc.status_code, content=error_body(code, str(exc.detail)))

    @app.exception_handler(Exception)
    async def _unexpected(_req: Request, exc: Exception) -> JSONResponse:  # pragma: no cover
        logger.exception("Unhandled error", exc_info=exc)
        return JSONResponse(status_code=500, content=error_body("INTERNAL_ERROR", "Lỗi hệ thống"))
