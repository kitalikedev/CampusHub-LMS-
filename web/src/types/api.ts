// Kiểu dữ liệu khớp với schema của API (06 §3). Thời gian là chuỗi ISO kèm "Z".

export type Role = "ADMIN" | "INSTRUCTOR" | "STUDENT";
export type SectionStatus = "DRAFT" | "PUBLISHED" | "LOCKED";
export type SubmissionMode = "SINGLE" | "OVERWRITE" | "MULTIPLE" | "OFFLINE";
export type LatePolicy = "REJECT" | "ACCEPT_MARK_LATE";
export type GradeVisibility = "IMMEDIATE" | "MANUAL";
export type AssignmentStatus = "NOT_SUBMITTED" | "SUBMITTED" | "LATE" | "GRADED" | "OFFLINE";
export type RegradeStatus = "PENDING" | "ACCEPTED" | "REJECTED";

export interface Page<T> {
  items: T[];
  total: number;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  student_code: string | null;
  is_active: boolean;
  must_change_password: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface UserBrief {
  id: number;
  email: string;
  full_name: string;
  student_code: string | null;
}

export interface UserWithPassword {
  user: User;
  temp_password: string;
}

export interface ImportedAccount {
  email: string;
  full_name: string;
  role: Role;
  student_code: string | null;
  temp_password: string;
}

export interface Semester {
  id: number;
  code: string;
  name: string;
  start_date: string;
  end_date: string;
  registration_start_at: string;
  registration_end_at: string;
  min_credits: number;
  max_credits: number;
  is_registration_open: boolean;
}

export interface SubjectBrief {
  id: number;
  code: string;
  name: string;
  credits: number;
  is_graded: boolean;
}

export interface Subject extends SubjectBrief {
  description: string | null;
  prerequisites: SubjectBrief[];
}

export interface Room {
  id: number;
  code: string;
  name: string;
  capacity: number;
}

export interface Slot {
  id: number;
  day_of_week: number;
  start_time: string;
  end_time: string;
  room: Room;
}

export interface Section {
  id: number;
  section_code: string;
  status: SectionStatus;
  capacity: number;
  enrolled_count: number;
  semester: { id: number; code: string; name: string };
  subject: SubjectBrief;
  prerequisites: SubjectBrief[];
  instructor: { id: number; full_name: string; email: string };
  slots: Slot[];
  locked_at: string | null;
  is_enrolled: boolean | null;
  registration_open: boolean;
}

export interface RosterRow {
  enrollment_id: number;
  source: "SELF" | "ADMIN";
  enrolled_at: string;
  student: UserBrief;
}

export interface Assignment {
  id: number;
  section_id: number;
  title: string;
  description: string | null;
  weight_percent: number;
  submission_mode: SubmissionMode;
  max_attempts: number | null;
  due_at: string | null;
  late_policy: LatePolicy | null;
  grade_visibility: GradeVisibility;
  grades_published_at: string | null;
  created_at: string;
}

export interface StoredFile {
  id: number;
  original_name: string;
  size_bytes: number;
}

export interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  attempt_no: number;
  content_url: string | null;
  file: StoredFile | null;
  is_late: boolean;
  submitted_at: string;
}

export interface GradeBrief {
  id: number;
  score: number;
  feedback: string | null;
  visible_at: string | null;
  updated_at: string;
}

export interface SubmissionRow {
  student: UserBrief;
  latest: Submission | null;
  attempts_count: number;
  grade: GradeBrief | null;
}

export interface CourseResult {
  final_score_10: number;
  letter_grade: string | null;
  grade_point: number | null;
  is_passed: boolean;
  finalized_at: string;
}

export interface Gradebook {
  section_id: number;
  status: SectionStatus;
  assignments: Assignment[];
  weight_total: number;
  rows: {
    student: UserBrief;
    scores: Record<string, number | null>;
    provisional_score: number | null;
    graded_weight: number;
    result: CourseResult | null;
  }[];
}

export interface MyGradeItem {
  assignment: Assignment;
  status: AssignmentStatus;
  visible: boolean;
  grade_hidden: boolean;
  attempts_count: number;
  latest: Submission | null;
  grade: GradeBrief | null;
  regrade: { id: number; status: RegradeStatus; new_score: number | null; response: string | null } | null;
}

export interface MyGrades {
  section_id: number;
  status: SectionStatus;
  items: MyGradeItem[];
  provisional_score: number | null;
  graded_weight: number;
  result: CourseResult | null;
}

export interface LockCheck {
  can_lock: boolean;
  checks: { key: string; ok: boolean; params: Record<string, unknown> }[];
}

export interface TranscriptCourse {
  section_id: number;
  section_code: string;
  subject_code: string;
  subject_name: string;
  credits: number;
  is_graded: boolean;
  status: "FINALIZED" | "IN_PROGRESS";
  score_10: number | null;
  letter_grade: string | null;
  grade_point: number | null;
  is_passed: boolean | null;
  provisional_score: number | null;
  graded_weight: number | null;
}

export interface Summary {
  gpa: number | null;
  average_10: number | null;
  gpa_credits: number;
  earned_credits: number;
}

export interface Transcript {
  student: UserBrief;
  semesters: (Summary & { semester: Semester; courses: TranscriptCourse[] })[];
  cumulative: Summary;
}

export interface ScheduleItem {
  section_id: number;
  section_code: string;
  subject_code: string;
  subject_name: string;
  instructor_name: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  room_code: string;
}

export interface Announcement {
  id: number;
  section_id: number;
  title: string;
  content: string;
  author: { id: number; full_name: string };
  created_at: string;
  updated_at: string;
}

export interface Dashboard {
  semester: Semester | null;
  sections: Section[];
  announcements: Announcement[];
  upcoming: { assignment: Assignment; section_code: string; status: AssignmentStatus }[];
  pending_grading: number | null;
  pending_regrades: number | null;
}

export interface RegradeView {
  request: {
    id: number;
    grade_id: number;
    reason: string;
    status: RegradeStatus;
    old_score: number;
    new_score: number | null;
    response: string | null;
    created_at: string;
    resolved_at: string | null;
  };
  assignment_id: number;
  assignment_title: string;
  section_id: number;
  section_code: string;
  subject_name: string;
  student: UserBrief;
  current_score: number;
}

export interface AppNotification {
  id: number;
  type: string;
  params: Record<string, string | number>;
  link: string | null;
  is_read: boolean;
  created_at: string;
}

export interface AuditLog {
  id: number;
  actor_id: number | null;
  action: string;
  entity_type: string;
  entity_id: number;
  before_data: unknown;
  after_data: unknown;
  reason: string | null;
  created_at: string;
}

export interface Stats {
  users_by_role: Record<string, number>;
  sections_by_status: Record<string, number>;
  letter_distribution: Record<string, number>;
  pass_rates: { subject_code: string; subject_name: string; finalized: number; passed: number }[];
}
