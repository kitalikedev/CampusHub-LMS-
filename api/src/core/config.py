"""Cấu hình đọc từ biến môi trường (NFR-SEC-01, NFR-SEC-06)."""
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

API_DIR = Path(__file__).resolve().parents[2]
load_dotenv(API_DIR / ".env")


def _split(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


class Settings:
    def __init__(self) -> None:
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "")
        if self.DATABASE_URL.startswith("sqlite:///./"):  # đường dẫn tương đối tính từ thư mục api/
            self.DATABASE_URL = "sqlite:///" + str(API_DIR / self.DATABASE_URL[len("sqlite:///./"):])
        self.JWT_SECRET: str = os.getenv("JWT_SECRET", "")
        self.JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
        self.BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "10"))
        self.CORS_ORIGINS: List[str] = _split(os.getenv("CORS_ORIGINS", "http://localhost:3000"))
        upload_dir = Path(os.getenv("UPLOAD_DIR", "storage/uploads"))
        self.UPLOAD_DIR: Path = upload_dir if upload_dir.is_absolute() else (API_DIR / upload_dir).resolve()
        self.MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "20"))
        self.REGRADE_WINDOW_DAYS: int = int(os.getenv("REGRADE_WINDOW_DAYS", "7"))

        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL chưa được cấu hình (xem api/.env.example)")
        if len(self.JWT_SECRET) < 32:
            raise RuntimeError("JWT_SECRET phải có ít nhất 32 ký tự (xem api/.env.example)")

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


settings = Settings()
