"use client";
import { Badge, Tone } from "@/components/ui";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Assignment, AssignmentStatus } from "@/types/api";

const tones: Record<AssignmentStatus, Tone> = {
  NOT_SUBMITTED: "neutral", SUBMITTED: "info", LATE: "warning", GRADED: "success", OFFLINE: "outline",
};

/** Nhãn trạng thái dùng chung (04 §4): luôn có chữ, không chỉ dùng màu. */
export function AssignmentStatusBadge({ status, hidden }: { status: AssignmentStatus; hidden?: boolean }) {
  const { t } = useI18n();
  return (
    <span className="inline-flex flex-wrap gap-1">
      <Badge tone={tones[status]}>{t(`status.assignment.${status}`)}</Badge>
      {hidden && <Badge tone="outline">{t("status.gradeHidden")}</Badge>}
    </span>
  );
}

/** Mô tả quy tắc nộp của bài: chế độ, số lần, hạn, chính sách trễ, chế độ hiện điểm. */
export function AssignmentRules({ assignment }: { assignment: Assignment }) {
  const { t, locale } = useI18n();
  const parts = [
    t(`modes.${assignment.submission_mode}`) +
      (assignment.submission_mode === "MULTIPLE" ? ` (${t("assignments.maxAttemptsShort", { n: assignment.max_attempts ?? 1 })})` : ""),
  ];
  if (assignment.due_at) parts.push(`${t("assignments.due")}: ${formatDateTime(assignment.due_at, locale)}`);
  if (assignment.late_policy) parts.push(t(`late.${assignment.late_policy}`));
  parts.push(t(`visibility.${assignment.grade_visibility}`));
  return <span className="text-sm text-muted">{parts.join(" · ")}</span>;
}
