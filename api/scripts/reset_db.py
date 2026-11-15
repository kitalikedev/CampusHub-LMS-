"""CHỈ DÙNG CHO DEV: xóa toàn bộ bảng của CampusHub v3, chạy lại migration và seed.

Chạy: python scripts/reset_db.py   (phải gõ RESET để xác nhận)
      python scripts/reset_db.py --yes   (bỏ qua xác nhận, dùng khi chạy tự động)
"""
import subprocess
import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_DIR))

from sqlalchemy import text  # noqa: E402

import src.models  # noqa: E402,F401
from src.core.db import Base, engine  # noqa: E402

if __name__ == "__main__":
    print(f"Sắp XÓA toàn bộ dữ liệu trong: {engine.url.render_as_string(hide_password=True)}")
    if "--yes" not in sys.argv and input("Gõ RESET để xác nhận: ").strip() != "RESET":
        print("Đã hủy.")
        sys.exit(1)
    Base.metadata.drop_all(engine)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
    subprocess.run([sys.executable, "scripts/init_db.py"], cwd=API_DIR, check=True)
    subprocess.run([sys.executable, "scripts/seed.py"], cwd=API_DIR, check=True)
