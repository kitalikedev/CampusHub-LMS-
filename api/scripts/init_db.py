"""Tạo database (nếu là MySQL và chưa có) rồi chạy migration tới bản mới nhất.

Chạy: python scripts/init_db.py
Không xóa dữ liệu nào.
"""
import subprocess
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402

from src.core.config import settings  # noqa: E402


def ensure_mysql_database() -> None:
    url = make_url(settings.DATABASE_URL)
    if not url.drivername.startswith("mysql") or not url.database:
        return
    server = create_engine(url.set(database=""))
    with server.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{url.database}` "
                          "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    print(f"Database '{url.database}' đã sẵn sàng.")


if __name__ == "__main__":
    ensure_mysql_database()
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=API_DIR, check=True)
    print("Migration xong.")
