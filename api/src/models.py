"""Nạp toàn bộ model để metadata đầy đủ (dùng cho Alembic, test, seed)."""
from src.modules.academics.models import GradeScale, Semester, Subject, subject_prerequisites  # noqa: F401
from src.modules.announcements.models import Announcement  # noqa: F401
from src.modules.assignments.models import Assignment  # noqa: F401
from src.modules.audit.models import AuditLog  # noqa: F401
from src.modules.enrollments.models import CourseResult, Enrollment  # noqa: F401
from src.modules.grading.models import Grade  # noqa: F401
from src.modules.notifications.models import Notification  # noqa: F401
from src.modules.regrades.models import RegradeRequest  # noqa: F401
from src.modules.rooms.models import Room  # noqa: F401
from src.modules.sections.models import CourseSection, ScheduleSlot  # noqa: F401
from src.modules.submissions.models import StoredFile, Submission  # noqa: F401
from src.modules.users.models import User  # noqa: F401
