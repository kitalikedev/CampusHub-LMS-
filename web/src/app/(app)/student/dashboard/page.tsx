"use client";
// SCR-S01 Tổng quan sinh viên (FR-DSH-01): số liệu thật, không gán cứng (ISS-16).
import Link from "next/link";

import { Card, EmptyState, ErrorState, PageHeader, SkeletonBlock, Stat, Table, Td, Th } from "@/components/ui";
import { AssignmentStatusBadge } from "@/features/assignments";
import { sectionTitle, SlotList } from "@/features/sections";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Dashboard } from "@/types/api";

export default function StudentDashboardPage() {
  return <RoleGate roles={["STUDENT"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t, locale } = useI18n();
  const dash = useApi<Dashboard>("/me/dashboard");
  if (dash.error) return <ErrorState error={dash.error} onRetry={dash.reload} />;
  if (!dash.data) return <SkeletonBlock rows={6} />;
  const { semester, sections, upcoming, announcements } = dash.data;
  const credits = sections.reduce((sum, s) => sum + s.subject.credits, 0);
  return (
    <>
      <PageHeader title={t("dashboard.studentTitle")} description={semester ? `${semester.code} · ${semester.name}` : undefined} />
      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Stat label={t("dashboard.classesThisTerm")} value={sections.length} hint={t("dashboard.credits", { n: credits })} />
        <Stat label={t("dashboard.dueSoon")} value={upcoming.length} hint={t("dashboard.dueSoonHint")} />
        <Stat label={t("dashboard.newAnnouncements")} value={announcements.length} />
      </div>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title={t("dashboard.dueSoon")}>
          {upcoming.length === 0 ? <EmptyState title={t("dashboard.noDue")} /> : (
            <Table>
              <thead><tr><Th>{t("assignments.title")}</Th><Th>{t("assignments.due")}</Th><Th>{t("common.status")}</Th></tr></thead>
              <tbody className="divide-y divide-line">
                {upcoming.map((u) => (
                  <tr key={u.assignment.id}>
                    <Td><Link className="font-medium text-navy-700 hover:underline" href={`/student/assignments/${u.assignment.id}`}>{u.assignment.title}</Link>
                      <span className="block text-xs text-muted">{u.section_code}</span></Td>
                    <Td>{formatDateTime(u.assignment.due_at, locale)}</Td>
                    <Td><AssignmentStatusBadge status={u.status} /></Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card>
        <Card title={t("dashboard.latestAnnouncements")}>
          {announcements.length === 0 ? <EmptyState title={t("announcements.empty")} /> : (
            <ul className="divide-y divide-line">
              {announcements.map((a) => (
                <li key={a.id} className="py-2">
                  <Link href={`/student/classes/${a.section_id}`} className="font-medium text-navy-700 hover:underline">{a.title}</Link>
                  <p className="text-xs text-muted">{a.author.full_name} · {formatDateTime(a.created_at, locale)}</p>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
      <Card title={t("dashboard.myClasses")} className="mt-4">
        {sections.length === 0 ? (
          <EmptyState title={t("dashboard.noClasses")} />
        ) : (
          <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {sections.map((s) => (
              <li key={s.id}>
                <Link href={`/student/classes/${s.id}`} className="block rounded-[var(--radius-control)] border border-line p-3 hover:border-navy-200">
                  <p className="font-medium text-ink">{sectionTitle(s)}</p>
                  <p className="text-xs text-muted">{s.instructor.full_name} · {t("common.creditsN", { n: s.subject.credits })}</p>
                  <div className="mt-1 text-xs text-muted"><SlotList slots={s.slots} /></div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </>
  );
}
