"use client";
// SCR-I03 Chi tiết lớp (GV): bài tập & trọng số, sổ điểm, sinh viên, thông báo, khóa sổ.
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Alert, Button, ConfirmDialog, EmptyState, ErrorState, PageHeader, SkeletonBlock, Table, Tabs, Td, Th,
         useErrorText, useToast } from "@/components/ui";
import { AnnouncementPanel } from "@/features/announcements";
import { AssignmentForm, AssignmentRules } from "@/features/assignments";
import { GradebookTable, LockPanel } from "@/features/grading";
import { SectionStatusBadge, sectionTitle, SlotList } from "@/features/sections";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime, formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Assignment, RosterRow, Section } from "@/types/api";

type Tab = "assignments" | "gradebook" | "students" | "announcements" | "lock";

export default function InstructorClassPage() {
  return <RoleGate roles={["INSTRUCTOR"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t } = useI18n();
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<Tab>("assignments");
  const section = useApi<Section>(`/sections/${id}`);
  if (section.error) return <ErrorState error={section.error} onRetry={section.reload} />;
  if (!section.data) return <SkeletonBlock rows={6} />;
  const s = section.data;
  return (
    <>
      <PageHeader title={sectionTitle(s)}
                  description={<span className="flex flex-wrap items-center gap-2"><SectionStatusBadge status={s.status} />
                    <span>{s.semester.code} · {t("sections.enrolledN", { n: s.enrolled_count, cap: s.capacity })}</span>
                    <span className="text-xs"><SlotList slots={s.slots} /></span></span>} />
      <Tabs value={tab} onChange={setTab} tabs={[
        { id: "assignments", label: t("classes.tabAssignments") }, { id: "gradebook", label: t("classes.tabGradebook") },
        { id: "students", label: t("classes.tabStudents") }, { id: "announcements", label: t("classes.tabAnnouncements") },
        { id: "lock", label: t("classes.tabLock") }]} />
      {tab === "assignments" && <AssignmentsTab section={s} />}
      {tab === "gradebook" && <GradebookTable sectionId={s.id} />}
      {tab === "students" && <StudentsTab sectionId={s.id} />}
      {tab === "announcements" && <AnnouncementPanel sectionId={s.id} canManage />}
      {tab === "lock" && <LockPanel sectionId={s.id} status={s.status} onLocked={section.reload} />}
    </>
  );
}

function AssignmentsTab({ section }: { section: Section }) {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const list = useApi<Assignment[]>(`/sections/${section.id}/assignments`);
  const [editing, setEditing] = useState<Assignment | "new" | null>(null);
  const [deleting, setDeleting] = useState<Assignment | null>(null);
  const locked = section.status === "LOCKED";
  const items = list.data ?? [];
  const total = items.reduce((sum, a) => sum + a.weight_percent, 0);
  const others = editing && editing !== "new" ? total - editing.weight_percent : total;

  async function remove() {
    if (!deleting) return;
    try {
      await api.delete(`/assignments/${deleting.id}`);
      toast(t("common.deleted"));
      list.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    }
    setDeleting(null);
  }

  if (list.error) return <ErrorState error={list.error} onRetry={list.reload} />;
  if (!list.data) return <SkeletonBlock />;
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <Alert tone={Math.abs(total - 100) < 0.001 ? "success" : "warning"}>
          {t("assignments.totalWeight", { total: formatNumber(total, locale, 2) })}
          {Math.abs(total - 100) >= 0.001 && ` · ${t("assignments.needs100")}`}
        </Alert>
        {!locked && <Button onClick={() => setEditing("new")}>{t("assignments.create")}</Button>}
      </div>
      {items.length === 0 ? <EmptyState title={t("assignments.empty")} /> : (
        <Table>
          <thead><tr><Th>{t("assignments.title")}</Th><Th>{t("assignments.weight")}</Th><Th>{t("assignments.rules")}</Th>
            <Th className="w-64">{t("common.actions")}</Th></tr></thead>
          <tbody className="divide-y divide-line">
            {items.map((a) => (
              <tr key={a.id}>
                <Td className="font-medium">{a.title}<span className="block text-xs text-muted">{t("assignments.createdAt", { at: formatDateTime(a.created_at, locale) })}</span></Td>
                <Td>{formatNumber(a.weight_percent, locale, 2)}%</Td>
                <Td><AssignmentRules assignment={a} /></Td>
                <Td>
                  <div className="flex flex-wrap gap-1">
                    <Link href={`/instructor/assignments/${a.id}`} className="inline-flex h-8 items-center rounded-[var(--radius-control)] bg-navy-900 px-3 text-sm font-medium text-white hover:bg-navy-800">
                      {t("grading.open")}</Link>
                    {!locked && <Button size="sm" variant="secondary" onClick={() => setEditing(a)}>{t("common.edit")}</Button>}
                    {!locked && <Button size="sm" variant="ghost" onClick={() => setDeleting(a)}>{t("common.delete")}</Button>}
                  </div>
                </Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      {editing && (
        <AssignmentForm sectionId={section.id} assignment={editing === "new" ? undefined : editing} weightUsed={others}
                        onClose={() => setEditing(null)} onSaved={() => { setEditing(null); list.reload(); }} />
      )}
      <ConfirmDialog open={deleting !== null} title={t("assignments.deleteTitle")} message={t("assignments.deleteText", { title: deleting?.title ?? "" })}
                     confirmLabel={t("common.delete")} danger onConfirm={remove} onClose={() => setDeleting(null)} />
    </div>
  );
}

function StudentsTab({ sectionId }: { sectionId: number }) {
  const { t, locale } = useI18n();
  const roster = useApi<RosterRow[]>(`/sections/${sectionId}/enrollments`);
  if (roster.error) return <ErrorState error={roster.error} onRetry={roster.reload} />;
  if (!roster.data) return <SkeletonBlock />;
  if (!roster.data.length) return <EmptyState title={t("gradebook.noStudents")} />;
  return (
    <Table>
      <thead><tr><Th>#</Th><Th>{t("users.studentCode")}</Th><Th>{t("users.fullName")}</Th><Th>{t("users.email")}</Th><Th>{t("sections.enrolledAt")}</Th></tr></thead>
      <tbody className="divide-y divide-line">
        {roster.data.map((r, index) => (
          <tr key={r.enrollment_id}>
            <Td>{index + 1}</Td><Td>{r.student.student_code}</Td><Td className="font-medium">{r.student.full_name}</Td>
            <Td>{r.student.email}</Td><Td>{formatDateTime(r.enrolled_at, locale)} · {t(`sections.source.${r.source}`)}</Td>
          </tr>
        ))}
      </tbody>
    </Table>
  );
}
