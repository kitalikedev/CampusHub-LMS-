"use client";
// SCR-S05 Chi tiết bài tập: nộp bài (FR-SUB-01…03), điểm, phúc khảo (FR-REG-01).
import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { Alert, Badge, Button, Card, ErrorState, Field, Input, PageHeader, SkeletonBlock, Table, Td, Textarea, Th,
         useErrorText, useToast } from "@/components/ui";
import { AssignmentRules, AssignmentStatusBadge } from "@/features/assignments";
import { api, downloadFile } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatBytes, formatDateTime, formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Assignment, MyGrades, Submission } from "@/types/api";

export default function StudentAssignmentPage() {
  return <RoleGate roles={["STUDENT"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const { id } = useParams<{ id: string }>();
  const assignment = useApi<Assignment>(`/assignments/${id}`);
  const sectionId = assignment.data?.section_id;
  const grades = useApi<MyGrades>(sectionId ? `/sections/${sectionId}/my-grades` : null);
  const attempts = useApi<Submission[]>(`/assignments/${id}/submissions/mine`);
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [submitError, setSubmitError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [reason, setReason] = useState("");
  const [regradeError, setRegradeError] = useState("");

  if (assignment.error) return <ErrorState error={assignment.error} onRetry={assignment.reload} />;
  if (!assignment.data || !grades.data) return <SkeletonBlock rows={6} />;
  const a = assignment.data;
  const item = grades.data.items.find((i) => i.assignment.id === a.id);
  const locked = grades.data.status === "LOCKED";
  const graded = item?.status === "GRADED" || Boolean(item?.grade_hidden);
  const overdue = a.due_at ? new Date(a.due_at) < new Date() : false;
  const canSubmit = a.submission_mode !== "OFFLINE" && !locked && !graded
    && !(a.submission_mode === "SINGLE" && (item?.attempts_count ?? 0) >= 1)
    && !(a.submission_mode === "MULTIPLE" && (item?.attempts_count ?? 0) >= (a.max_attempts ?? 1))
    && !(overdue && a.late_policy === "REJECT");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSubmitError("");
    setSubmitting(true);
    const form = new FormData();
    if (url.trim()) form.append("content_url", url.trim());
    if (file) form.append("file", file);
    try {
      const r = await api.post<Submission>(`/assignments/${a.id}/submissions`, form);
      toast(r.data.is_late ? t("submit.doneLate") : t("submit.done"));
      setUrl("");
      setFile(null);
      attempts.reload();
      grades.reload();
    } catch (err) {
      setSubmitError(errorText(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function requestRegrade(event: FormEvent) {
    event.preventDefault();
    if (!item?.grade) return;
    setRegradeError("");
    try {
      await api.post(`/grades/${item.grade.id}/regrade-requests`, { reason });
      toast(t("regrades.sent"));
      setReason("");
      grades.reload();
    } catch (err) {
      setRegradeError(errorText(err));
    }
  }

  return (
    <>
      <PageHeader title={a.title} description={<AssignmentRules assignment={a} />}
                  actions={<Link href={`/student/classes/${a.section_id}`} className="text-sm text-navy-700 hover:underline">{t("common.backToClass")}</Link>} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <Card title={t("assignments.description")}>
            <p className="whitespace-pre-line text-sm text-ink">{a.description || t("assignments.noDescription")}</p>
            <p className="mt-3 text-sm text-muted">{t("assignments.weight")}: {formatNumber(a.weight_percent, locale, 0)}%</p>
          </Card>
          <Card title={t("submit.title")}>
            {a.submission_mode === "OFFLINE" ? <Alert tone="info">{t("submit.offline")}</Alert>
              : locked ? <Alert tone="info">{t("submit.locked")}</Alert>
              : graded ? <Alert tone="info">{t("submit.graded")}</Alert>
              : !canSubmit ? <Alert tone="warning">{overdue && a.late_policy === "REJECT" ? t("submit.pastDue") : t("submit.limit")}</Alert>
              : (
                <form onSubmit={submit} className="space-y-3">
                  {overdue && <Alert tone="warning">{t("submit.willBeLate")}</Alert>}
                  {submitError && <Alert tone="danger">{submitError}</Alert>}
                  <Field label={t("submit.url")} hint={t("submit.urlHint")}>
                    {(p) => <Input {...p} type="url" placeholder="https://github.com/…" value={url} onChange={(e) => setUrl(e.target.value)} />}
                  </Field>
                  <Field label={t("submit.file")} hint={t("submit.fileHint")}>
                    {(p) => <Input {...p} type="file" accept=".pdf,.docx,.pptx,.xlsx,.zip,.rar,.txt"
                                   onChange={(e) => setFile(e.target.files?.[0] ?? null)} />}
                  </Field>
                  <Button type="submit" loading={submitting} disabled={!url.trim() && !file}>
                    {(item?.attempts_count ?? 0) > 0 ? t("submit.resubmit") : t("submit.action")}
                  </Button>
                </form>
              )}
          </Card>
          <Card title={t("submit.history")}>
            {!attempts.data?.length ? <p className="text-sm text-muted">{t("submit.none")}</p> : (
              <Table>
                <thead><tr><Th>{t("submit.attempt")}</Th><Th>{t("submit.when")}</Th><Th>{t("submit.content")}</Th></tr></thead>
                <tbody className="divide-y divide-line">
                  {attempts.data.map((s) => (
                    <tr key={s.id}>
                      <Td>#{s.attempt_no} {s.is_late && <Badge tone="warning">{t("status.assignment.LATE")}</Badge>}</Td>
                      <Td>{formatDateTime(s.submitted_at, locale)}</Td>
                      <Td className="space-y-1 break-all">
                        {s.content_url && <a href={s.content_url} target="_blank" rel="noreferrer" className="block text-navy-700 hover:underline">{s.content_url}</a>}
                        {s.file && <button type="button" className="text-navy-700 hover:underline" onClick={() => downloadFile(s.file!.id, s.file!.original_name)}>
                          {s.file.original_name} ({formatBytes(s.file.size_bytes)})</button>}
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </Card>
        </div>
        <Card title={t("assignments.score")}>
          {item && <AssignmentStatusBadge status={item.status} hidden={item.grade_hidden} />}
          {item?.grade ? (
            <div className="mt-3 space-y-3">
              <p className="text-3xl font-semibold text-ink">{formatNumber(item.grade.score, locale)}<span className="text-base text-muted"> / 10</span></p>
              {item.grade.feedback && <p className="whitespace-pre-line rounded-[var(--radius-control)] bg-surface p-3 text-sm">{item.grade.feedback}</p>}
              {item.regrade ? (
                <Alert tone={item.regrade.status === "PENDING" ? "info" : item.regrade.status === "ACCEPTED" ? "success" : "warning"}
                       title={t(`status.regrade.${item.regrade.status}`)}>
                  {item.regrade.response}
                </Alert>
              ) : !locked && (
                <form onSubmit={requestRegrade} className="space-y-2 border-t border-line pt-3">
                  {regradeError && <Alert tone="danger">{regradeError}</Alert>}
                  <Field label={t("regrades.reason")} hint={t("regrades.windowHint")} required>
                    {(p) => <Textarea {...p} required value={reason} onChange={(e) => setReason(e.target.value)} />}
                  </Field>
                  <Button type="submit" variant="secondary" size="sm">{t("regrades.request")}</Button>
                </form>
              )}
            </div>
          ) : (
            <p className="mt-3 text-sm text-muted">{item?.grade_hidden ? t("status.gradeHiddenText") : t("assignments.noScore")}</p>
          )}
        </Card>
      </div>
    </>
  );
}
