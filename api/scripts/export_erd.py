"""Sinh bản nháp ERD dạng draw.io (crow's foot) từ model SQLAlchemy, để sơ đồ luôn khớp code.

Chạy:  python scripts/export_erd.py
Ra:    docs/diagrams/to-be/ERD-01.drawio      (18 bảng, đọc từ src/models)
       docs/diagrams/as-is/ERD-ASIS-01.drawio (7 bảng của hệ thống cũ, theo 01-AS-IS §4)

Mở file bằng draw.io (desktop hoặc app.diagrams.net) để chỉnh bố cục và xuất PNG.
Khi đổi model: chạy lại script, rồi chỉnh lại bố cục nếu cần (07-DIAGRAMS §6).
"""
import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple
from xml.sax.saxutils import escape as _escape

API_DIR = Path(__file__).resolve().parents[1]
ROOT = API_DIR.parent
sys.path.insert(0, str(API_DIR))

from sqlalchemy import Enum, UniqueConstraint  # noqa: E402
from sqlalchemy.dialects import mysql  # noqa: E402

import src.models  # noqa: E402,F401
from src.core.db import Base  # noqa: E402

ROW_H = 26


def escape(text: str) -> str:
    """Thoát ký tự cho giá trị thuộc tính XML (kể cả dấu ")."""
    return _escape(text, {'"': "&quot;"})

HEAD_H = 32
KEY_W = 54


class Col(NamedTuple):
    name: str
    type: str
    keys: str  # "PK", "FK", "PK,FK", "UQ", "FK,UQ", ""
    nullable: bool


class Table(NamedTuple):
    name: str
    columns: List[Col]
    notes: List[str]  # dòng ghi chú cuối bảng, ví dụ UQ ghép


class Rel(NamedTuple):
    child: str
    child_col: str
    parent: str
    parent_col: str
    child_many: bool  # False: quan hệ 1–1 (FK là PK hoặc UNIQUE)
    parent_optional: bool  # FK cho phép NULL


# ---------------------------------------------------------------------------------------------
# Đọc model
# ---------------------------------------------------------------------------------------------

def _type_label(column) -> str:
    if isinstance(column.type, Enum):
        return "ENUM(" + "/".join(column.type.enums) + ")"
    return column.type.compile(dialect=mysql.dialect()).replace("TINYINT(1)", "BOOL")


def from_metadata() -> Tuple[List[Table], List[Rel]]:
    tables: List[Table] = []
    rels: List[Rel] = []
    for table in Base.metadata.sorted_tables:
        single_unique = {list(c.columns)[0].name for c in table.constraints
                         if isinstance(c, UniqueConstraint) and len(c.columns) == 1}
        notes = ["UQ(" + ", ".join(col.name for col in c.columns) + ")" for c in table.constraints
                 if isinstance(c, UniqueConstraint) and len(c.columns) > 1]
        pk_cols = [c.name for c in table.primary_key.columns]
        if len(pk_cols) > 1:
            notes.insert(0, "PK(" + ", ".join(pk_cols) + ")")
        cols: List[Col] = []
        for column in table.columns:
            keys = []
            if column.primary_key:
                keys.append("PK")
            if column.foreign_keys:
                keys.append("FK")
            if (column.unique or column.name in single_unique) and not column.primary_key:
                keys.append("UQ")
            cols.append(Col(column.name, _type_label(column), ",".join(keys), bool(column.nullable)))
            for fk in column.foreign_keys:
                one_to_one = (column.primary_key and len(pk_cols) == 1) or column.unique \
                    or column.name in single_unique
                rels.append(Rel(table.name, column.name, fk.column.table.name, fk.column.name,
                                child_many=not one_to_one, parent_optional=bool(column.nullable)))
        tables.append(Table(table.name, cols, notes))
    return tables, rels


def as_is() -> Tuple[List[Table], List[Rel]]:
    """7 bảng của hệ thống hiện tại (01-AS-IS §4)."""
    def c(name, type_, keys="", nullable=False):
        return Col(name, type_, keys, nullable)

    tables = [
        Table("users", [c("id", "INTEGER", "PK"), c("name", "VARCHAR(255)"), c("email", "VARCHAR(255)", "UQ"),
                        c("password_hash", "VARCHAR(255)"), c("role", "ENUM(ADMIN/INSTRUCTOR/STUDENT)"),
                        c("created_at", "DATETIME"), c("updated_at", "DATETIME")], []),
        Table("courses", [c("id", "INTEGER", "PK"), c("instructor_id", "INTEGER", "FK"), c("title", "VARCHAR(255)"),
                          c("description", "TEXT"), c("created_at", "DATETIME"), c("updated_at", "DATETIME")], []),
        Table("enrollments", [c("student_id", "INTEGER", "PK,FK"), c("course_id", "INTEGER", "PK,FK"),
                              c("enrolled_at", "DATETIME")], ["PK(student_id, course_id)"]),
        Table("assignments", [c("id", "INTEGER", "PK"), c("course_id", "INTEGER", "FK"), c("title", "VARCHAR(255)"),
                              c("description", "TEXT"), c("due_date", "DATETIME"), c("weight", "INTEGER"),
                              c("created_at", "DATETIME")], []),
        Table("submissions", [c("id", "INTEGER", "PK"), c("assignment_id", "INTEGER", "FK"),
                              c("student_id", "INTEGER", "FK"), c("content_url", "TEXT"),
                              c("grade", "INTEGER", nullable=True), c("feedback", "TEXT", nullable=True),
                              c("submitted_at", "DATETIME")],
              ["ISS-03: không có UQ(assignment_id, student_id)", "→ nộp lại tạo bản ghi trùng, điểm bị \"lạc\""]),
        Table("announcements", [c("id", "INTEGER", "PK"), c("course_id", "INTEGER", "FK"),
                                c("author_id", "INTEGER", "FK"), c("title", "VARCHAR(255)"), c("content", "TEXT"),
                                c("created_at", "DATETIME")], []),
        Table("schedules", [c("id", "INTEGER", "PK"), c("course_id", "INTEGER", "FK"),
                            c("day_of_week", "VARCHAR(20)"), c("start_time", "VARCHAR(10)"),
                            c("end_time", "VARCHAR(10)"), c("room", "VARCHAR(50)")],
              ["Giờ và phòng lưu dạng chuỗi tự do"]),
    ]
    rels = [
        Rel("courses", "instructor_id", "users", "id", True, False),
        Rel("enrollments", "student_id", "users", "id", True, False),
        Rel("enrollments", "course_id", "courses", "id", True, False),
        Rel("assignments", "course_id", "courses", "id", True, False),
        Rel("submissions", "assignment_id", "assignments", "id", True, False),
        Rel("submissions", "student_id", "users", "id", True, False),
        Rel("announcements", "course_id", "courses", "id", True, False),
        Rel("announcements", "author_id", "users", "id", True, False),
        Rel("schedules", "course_id", "courses", "id", True, False),
    ]
    return tables, rels


# ---------------------------------------------------------------------------------------------
# Xuất draw.io
# ---------------------------------------------------------------------------------------------

def _width(table: Table) -> int:
    longest = max([len(f"{c.name} : {c.type}") for c in table.columns] + [len(n) for n in table.notes] + [10])
    return max(240, min(440, KEY_W + 16 + int(longest * 6.6)))


def _height(table: Table) -> int:
    return HEAD_H + ROW_H * (len(table.columns) + len(table.notes))


TABLE_STYLE = ("shape=table;startSize={head};container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;"
               "rowLines=0;fontStyle=1;align=center;resizeLast=1;html=1;whiteSpace=wrap;"
               "fillColor={fill};strokeColor=#0B2545;fontColor=#0B2545;fontSize=13;")
ROW_STYLE = ("shape=tableRow;horizontal=0;startSize=0;swimlaneHead=0;swimlaneBody=0;fillColor=none;collapsible=0;"
             "dropTarget=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;top=0;left=0;right=0;bottom={bottom};"
             "html=1;strokeColor=#B9C8DE;")
CELL_STYLE = ("shape=partialRectangle;connectable=0;fillColor=none;top=0;left=0;bottom=0;right=0;overflow=hidden;"
              "html=1;whiteSpace=wrap;fontSize=11;fontColor=#0B2545;{extra}")


def render(tables: List[Table], rels: List[Rel], layout: List[List[str]], info: List[str],
           diagram_name: str, fill: str = "#EEF2F8") -> str:
    by_name = {t.name: t for t in tables}
    missing = set(by_name) - {n for col in layout for n in col}
    if missing:
        layout = layout + [sorted(missing)]
    cells: List[str] = []
    row_id: Dict[Tuple[str, str], str] = {}
    gap_x, gap_y, x = 90, 50, 40
    top = 40 + 30 * len(info) + 40
    for column in layout:
        y = top
        width = max(_width(by_name[n]) for n in column)
        for name in column:
            table = by_name[name]
            tid = f"t_{name}"
            height = _height(table)
            cells.append(f'<mxCell id="{tid}" value="{escape(name)}" style="{TABLE_STYLE.format(head=HEAD_H, fill=fill)}" '
                         f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{width}" height="{height}" '
                         f'as="geometry"/></mxCell>')
            rows = [(c.keys, f"{c.name} : {c.type}" + ("" if not c.nullable or "PK" in c.keys else " NULL"),
                     "PK" in c.keys, c.name) for c in table.columns]
            rows += [("", note, False, None) for note in table.notes]
            for index, (keys, label, is_pk, col_name) in enumerate(rows):
                rid = f"{tid}_r{index}"
                if col_name:
                    row_id[(name, col_name)] = rid
                last = index == len(table.columns) - 1 and table.notes
                cells.append(f'<mxCell id="{rid}" value="" style="{ROW_STYLE.format(bottom=1 if (is_pk or last) else 0)}" '
                             f'vertex="1" parent="{tid}"><mxGeometry y="{HEAD_H + index * ROW_H}" width="{width}" '
                             f'height="{ROW_H}" as="geometry"/></mxCell>')
                key_style = CELL_STYLE.format(extra="fontStyle=1;align=center;")
                cells.append(f'<mxCell id="{rid}_k" value="{escape(keys)}" style="{key_style}" vertex="1" parent="{rid}">'
                             f'<mxGeometry width="{KEY_W}" height="{ROW_H}" as="geometry">'
                             f'<mxRectangle width="{KEY_W}" height="{ROW_H}" as="alternateBounds"/></mxGeometry></mxCell>')
                font = "fontStyle=4;" if is_pk else ("fontStyle=2;fontColor=#475569;" if col_name is None else "")
                text_style = CELL_STYLE.format(extra=f"align=left;spacingLeft=6;{font}")
                cells.append(f'<mxCell id="{rid}_v" value="{escape(label)}" style="{text_style}" vertex="1" parent="{rid}">'
                             f'<mxGeometry x="{KEY_W}" width="{width - KEY_W}" height="{ROW_H}" as="geometry">'
                             f'<mxRectangle width="{width - KEY_W}" height="{ROW_H}" as="alternateBounds"/>'
                             f'</mxGeometry></mxCell>')
            y += height + gap_y
        x += width + gap_x
    for index, rel in enumerate(rels):
        source = row_id[(rel.child, rel.child_col)]
        target = row_id[(rel.parent, rel.parent_col)]
        start = "ERzeroToMany" if rel.child_many else "ERzeroToOne"
        end = "ERzeroToOne" if rel.parent_optional else "ERmandOne"
        style = (f"edgeStyle=entityRelationEdgeStyle;html=1;rounded=0;startArrow={start};endArrow={end};"
                 "startFill=0;endFill=0;strokeColor=#134074;fontSize=10;fontColor=#475569;")
        cells.append(f'<mxCell id="e{index}" value="{escape(rel.child_col)}" style="{style}" edge="1" parent="1" '
                     f'source="{source}" target="{target}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    info_html = "<br>".join(escape(line) for line in info)
    cells.append(f'<mxCell id="info" value="{escape(info_html)}" style="rounded=0;whiteSpace=wrap;html=1;align=left;'
                 f'verticalAlign=top;spacingLeft=8;spacingTop=6;fillColor=#FFFFFF;strokeColor=#0B2545;fontSize=12;" '
                 f'vertex="1" parent="1"><mxGeometry x="40" y="20" width="900" height="{30 * len(info) + 20}" '
                 f'as="geometry"/></mxCell>')
    body = "".join(cells)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<mxfile host="CampusHub export_erd.py" type="device">'
            f'<diagram id="{diagram_name}" name="{escape(diagram_name)}">'
            '<mxGraphModel dx="1600" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
            'fold="1" page="0" pageScale="1" pageWidth="1600" pageHeight="1200" math="0" shadow="0"><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>'
            f'{body}</root></mxGraphModel></diagram></mxfile>\n')


LEGEND = "Ký hiệu: PK khóa chính (gạch chân) · FK khóa ngoại · UQ duy nhất · NULL cho phép rỗng · crow's foot: |0 = 0..1 · || = đúng 1 · 0< = 0..n"

TO_BE_LAYOUT = [
    ["users", "notifications", "audit_logs"],
    ["semesters", "subjects", "subject_prerequisites", "grade_scales"],
    ["course_sections", "schedule_slots", "rooms"],
    ["enrollments", "course_results", "announcements"],
    ["assignments", "submissions", "files"],
    ["grades", "regrade_requests"],
]
AS_IS_LAYOUT = [["users"], ["courses", "enrollments"], ["assignments", "schedules"], ["submissions", "announcements"]]


def main() -> None:
    today = date.today().isoformat()
    tables, rels = from_metadata()
    to_be = render(tables, rels, TO_BE_LAYOUT, [
        "ERD-01 · ERD hệ thống CampusHub v3 (to-be) · phiên bản 0.1 (bản nháp sinh từ code) · " + today,
        f"Nguồn: api/src/modules/*/models.py = migration 0001_initial_schema · {len(tables)} bảng · {len(rels)} quan hệ",
        "Người vẽ/duyệt: TV2 / Lead · Liên quan: 05-DATA-MODEL §2, BR-ENR-09, BR-SUB-08, BR-GRD-02, BR-REG-02, BR-LCK-04",
        LEGEND,
    ], "ERD-01")
    out = ROOT / "docs" / "diagrams" / "to-be" / "ERD-01.drawio"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(to_be, encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(tables)} bảng, {len(rels)} quan hệ")

    old_tables, old_rels = as_is()
    legacy = render(old_tables, old_rels, AS_IS_LAYOUT, [
        "ERD-ASIS-01 · ERD hệ thống hiện tại (as-is, trước khi làm lại) · phiên bản 0.1 · " + today,
        "Nguồn: 01-AS-IS §4 (code cũ, bản sao lưu ở _backup/) · 7 bảng",
        "Điểm yếu: không có học kỳ/tín chỉ; điểm nằm trong submissions (ISS-03); lịch học lưu chuỗi tự do",
        LEGEND,
    ], "ERD-ASIS-01", fill="#FFF7ED")
    out = ROOT / "docs" / "diagrams" / "as-is" / "ERD-ASIS-01.drawio"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(legacy, encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {len(old_tables)} bảng, {len(old_rels)} quan hệ")


if __name__ == "__main__":
    main()
