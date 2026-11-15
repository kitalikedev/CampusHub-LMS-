"use client";
// SCR-S04 Chi tiết lớp (SV): thông báo, bài tập & điểm (FR-GRD-04, AC-SUB-03.1).
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import { Alert, Card, DefinitionList, ErrorState, PageHeader, SkeletonBlock, Table, Tabs, Td, Th } from "@/components/ui";
import { AnnouncementPanel } from "@/features/announcements";
import { AssignmentStatusBadge } from "@/features/assignments";
import { SectionStatusBadge, sectionTitle, SlotList } from "@/features/sections";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime, formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { MyGrades, Section } from "@/types/api";

export default function StudentClassPage() {
  return <RoleGate roles={["STUDENT"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t, locale } = useI18n();
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<"work" | "announcements">("work");
  const section = useApi<Section>(`/sections/${id}`);
  const grades = useApi<MyGrades>(section.data?.is_enrolled ? `/sections/${id}/my-grades` : null);

  if (section.error) return <ErrorState error={section.error} onRetry={section.reload} />;
  if (!section.data) return <SkeletonBlock rows={6} />;
  const s = section.data;
  return (
    <>
      <PageHeader title={sectionTitle(s)} description={<SectionStatusBadge status={s.status} />} />
      <Card className="mb-5">
        <DefinitionList items={[
          { label: t("semesters.label"), value: `${s.semester.code} · ${s.semester.name}` },
          { label: t("sections.instructor"), value: `${s.instructor.full_name} (${s.instructor.email})` },
          { label: t("subjects.credits"), value: s.subject.credits },
          { label: t("sections.schedule"), value: <SlotList slots={s.slots} /> },
        ]} />
      </Card>
      {!s.is_enrolled ? (
        <Alert tone="info">{t("classes.notEnrolled")}</Alert>
      ) : (
        <>
          <Tabs value={tab} onChange={setTab} tabs={[
            { id: "work", label: t("classes.tabWork") }, { id: "announcements", label: t("classes.tabAnnouncements") }]} />
          {tab === "announcements" && <AnnouncementPanel sectionId={s.id} canManage={false} />}
          {tab === "work" && (
            <>
              {grades.error && <ErrorState error={grades.error} onRetry={grades.reload} />}
              {!grades.data && !grades.error && <SkeletonBlock />}
              {grades.data && (
                <div className="space-y-4">
                  {grades.data.result ? (
                    <Alert tone={grades.data.result.is_passed ? "success" : "danger"} title={t("classes.finalResult")}>
                      {t("classes.resultText", {
                        score: formatNumber(grades.data.result.final_score_10, locale),
                        letter: grades.data.result.letter_grade ?? (grades.data.result.is_passed ? t("transcript.pass") : t("transcript.fail")),
                      })}
                    </Alert>
                  ) : (
                    <Alert tone="info">
                      {grades.data.provisional_score === null ? t("classes.noProvisional") : t("classes.provisional", {
                        score: formatNumber(grades.data.provisional_score, locale),
                        w: formatNumber(grades.data.graded_weight, locale, 0) })}
                    </Alert>
                  )}
                  <Table>
                    <thead><tr><Th>{t("assignments.title")}</Th><Th>{t("assignments.weight")}</Th><Th>{t("assignments.due")}</Th>
                      <Th>{t("common.status")}</Th><Th className="text-right">{t("assignments.score")}</Th></tr></thead>
                    <tbody className="divide-y divide-line">
                      {grades.data.items.map((item) => (
                        <tr key={item.assignment.id}>
                          <Td><Link href={`/student/assignments/${item.assignment.id}`} className="font-medium text-navy-700 hover:underline">{item.assignment.title}</Link>
                            <span className="block text-xs text-muted">{t(`modes.${item.assignment.submission_mode}`)}</span></Td>
                          <Td>{formatNumber(item.assignment.weight_percent, locale, 0)}%</Td>
                          <Td>{formatDateTime(item.assignment.due_at, locale)}</Td>
                          <Td><AssignmentStatusBadge status={item.status} hidden={item.grade_hidden} /></Td>
                          <Td className="text-right tabular-nums">{item.grade ? formatNumber(item.grade.score, locale) : "—"}</Td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              )}
            </>
          )}
        </>
      )}
    </>
  );
}
