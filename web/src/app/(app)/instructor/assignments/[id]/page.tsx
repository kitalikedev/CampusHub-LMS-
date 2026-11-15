"use client";
// SCR-I04 Chấm bài (FR-SUB-04, FR-GRD-01, 02): mọi SV của lớp, bài nộp mới nhất, điểm 0–10, công bố.
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Alert, Badge, Button, ConfirmDialog, EmptyState, ErrorState, Input, PageHeader, SkeletonBlock, Table, Td,
         Textarea, Th, useErrorText, useToast } from "@/components/ui";
import { AssignmentRules } from "@/features/assignments";
import { api, downloadFile } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime, formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Assignment, Section, SubmissionRow } from "@/types/api";

export default function GradingPage() {
  return <RoleGate roles={["INSTRUCTOR"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const { id } = useParams<{ id: string }>();
  const assignment = useApi<Assignment>(`/assignments/${id}`);
  const section = useApi<Section>(assignment.data ? `/sections/${assignment.data.section_id}` : null);
  const rows = useApi<SubmissionRow[]>(`/assignments/${id}/submissions`);
  const [publishing, setPublishing] = useState(false);
  const [confirm, setConfirm] = useState(false);

  if (assignment.error) return <ErrorState error={assignment.error} onRetry={assignment.reload} />;
  if (rows.error) return <ErrorState error={rows.error} onRetry={rows.reload} />;
  if (!assignment.data || !rows.data || !section.data) return <SkeletonBlock rows={6} />;
  const a = assignment.data;
  const locked = section.data.status === "LOCKED";
  const manualPending = a.grade_visibility === "MANUAL" && !a.grades_published_at;

  async function publish() {
    setPublishing(true);
    try {
      await api.post(`/assignments/${a.id}/publish-grades`);
      toast(t("grading.published"));
      setConfirm(false);
      assignment.reload();
      rows.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    } finally {
      setPublishing(false);
    }
  }

  const submitted = rows.data.filter((r) => r.latest).length;
  const graded = rows.data.filter((r) => r.grade).length;
  return (
    <>
      <PageHeader title={a.title} description={<AssignmentRules assignment={a} />}
                  actions={<>
                    <Link href={`/instructor/classes/${a.section_id}`} className="text-sm text-navy-700 hover:underline">{t("common.backToClass")}</Link>
                    {manualPending && !locked && <Button onClick={() => setConfirm(true)}>{t("grading.publish")}</Button>}
                  </>} />
      <div className="mb-4 space-y-2">
        <Alert tone="info">{t("grading.summary", { submitted, graded, total: rows.data.length })}</Alert>
        {manualPending && <Alert tone="warning">{t("grading.manualHint")}</Alert>}
        {locked && <Alert tone="info">{t("lock.lockedText")}</Alert>}
      </div>
      {rows.data.length === 0 ? <EmptyState title={t("gradebook.noStudents")} /> : (
        <Table>
          <thead><tr><Th>{t("gradebook.student")}</Th><Th>{t("grading.submission")}</Th><Th className="w-32">{t("grading.score")}</Th>
            <Th>{t("grading.feedback")}</Th><Th className="w-28" /></tr></thead>
          <tbody className="divide-y divide-line">
            {rows.data.map((row) => (
              <GradeRow key={`${row.student.id}-${row.grade?.updated_at ?? "none"}`} row={row} assignment={a}
                        locked={locked} onSaved={rows.reload} />
            ))}
          </tbody>
        </Table>
      )}
      <ConfirmDialog open={confirm} title={t("grading.publishTitle")} message={t("grading.publishText")}
                     confirmLabel={t("grading.publish")} loading={publishing} onConfirm={publish} onClose={() => setConfirm(false)} />
    </>
  );
}

function GradeRow({ row, assignment, locked, onSaved }: {
  row: SubmissionRow; assignment: Assignment; locked: boolean; onSaved: () => void;
}) {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const [score, setScore] = useState(row.grade ? String(row.grade.score) : "");
  const [feedback, setFeedback] = useState(row.grade?.feedback ?? "");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const sub = row.latest;

  async function save() {
    setSaving(true);
    setError("");
    try {
      await api.put(`/assignments/${assignment.id}/grades/${row.student.id}`, { score: score === "" ? null : Number(score), feedback });
      toast(t("grading.saved", { name: row.student.full_name }));
      onSaved();
    } catch (err) {
      setError(errorText(err));
      setSaving(false);
    }
  }

  return (
    <tr>
      <Td><p className="font-medium">{row.student.full_name}</p><p className="text-xs text-muted">{row.student.student_code}</p></Td>
      <Td className="max-w-xs space-y-1 break-all text-xs">
        {assignment.submission_mode === "OFFLINE" ? <Badge tone="outline">{t("status.assignment.OFFLINE")}</Badge>
          : !sub ? <Badge>{t("status.assignment.NOT_SUBMITTED")}</Badge> : (
            <>
              <p>{formatDateTime(sub.submitted_at, locale)} {sub.is_late && <Badge tone="warning">{t("status.assignment.LATE")}</Badge>}
                {row.attempts_count > 1 && <span className="text-muted"> · {t("grading.attempts", { n: row.attempts_count })}</span>}</p>
              {sub.content_url && <a href={sub.content_url} target="_blank" rel="noreferrer" className="block text-navy-700 hover:underline">{sub.content_url}</a>}
              {sub.file && <button type="button" className="text-navy-700 hover:underline" onClick={() => downloadFile(sub.file!.id, sub.file!.original_name)}>{sub.file.original_name}</button>}
            </>
          )}
      </Td>
      <Td>
        <Input type="number" min={0} max={10} step={0.01} value={score} disabled={locked}
               aria-label={t("grading.scoreFor", { name: row.student.full_name })} onChange={(e) => setScore(e.target.value)} />
        {row.grade && !row.grade.visible_at && <span className="mt-1 block text-xs text-muted">{t("status.gradeHidden")}</span>}
        {row.grade && <span className="block text-xs text-muted">{t("grading.current", { score: formatNumber(row.grade.score, locale) })}</span>}
      </Td>
      <Td><Textarea rows={2} value={feedback} disabled={locked} aria-label={t("grading.feedback")} onChange={(e) => setFeedback(e.target.value)} />
        {error && <p className="mt-1 text-xs text-danger" role="alert">{error}</p>}</Td>
      <Td>{!locked && <Button size="sm" loading={saving} disabled={score === ""} onClick={save}>{t("common.save")}</Button>}</Td>
    </tr>
  );
}
