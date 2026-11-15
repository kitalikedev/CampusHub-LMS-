"use client";
// SCR-S07 Bảng điểm (FR-TRN-01; BR-TRN-01…07): GPA theo tín chỉ, môn đang học không tính.
import Link from "next/link";

import { Alert, Badge, Card, EmptyState, ErrorState, PageHeader, SkeletonBlock, Stat, Table, Td, Th } from "@/components/ui";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Transcript } from "@/types/api";

export default function TranscriptPage() {
  return <RoleGate roles={["STUDENT"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t, locale } = useI18n();
  const data = useApi<Transcript>("/me/transcript");
  if (data.error) return <ErrorState error={data.error} onRetry={data.reload} />;
  if (!data.data) return <SkeletonBlock rows={8} />;
  const { cumulative, semesters, student } = data.data;
  return (
    <>
      <PageHeader title={t("transcript.title")} description={`${student.full_name} · ${student.student_code ?? ""}`} />
      <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Stat label={t("transcript.cumulativeGpa")} value={formatNumber(cumulative.gpa, locale)} hint={t("transcript.scale4")} />
        <Stat label={t("transcript.cumulativeAvg")} value={formatNumber(cumulative.average_10, locale)} hint={t("transcript.scale10")} />
        <Stat label={t("transcript.earnedCredits")} value={cumulative.earned_credits}
              hint={t("transcript.gpaCredits", { n: cumulative.gpa_credits })} />
      </div>
      <Alert tone="info">{t("transcript.rules")}</Alert>
      {semesters.length === 0 && <div className="mt-4"><EmptyState title={t("transcript.empty")} /></div>}
      <div className="mt-4 space-y-4">
        {[...semesters].reverse().map((term) => (
          <Card key={term.semester.id} title={`${term.semester.code} · ${term.semester.name}`}
                actions={<span className="text-sm text-muted">
                  {t("transcript.termSummary", { gpa: formatNumber(term.gpa, locale), avg: formatNumber(term.average_10, locale), n: term.earned_credits })}
                </span>}>
            <Table>
              <thead><tr><Th>{t("subjects.subject")}</Th><Th>{t("subjects.credits")}</Th><Th className="text-right">{t("transcript.score10")}</Th>
                <Th>{t("transcript.letter")}</Th><Th className="text-right">{t("transcript.point4")}</Th><Th>{t("common.status")}</Th></tr></thead>
              <tbody className="divide-y divide-line">
                {term.courses.map((c) => (
                  <tr key={c.section_id}>
                    <Td><Link href={`/student/classes/${c.section_id}`} className="font-medium text-navy-700 hover:underline">{c.subject_code}</Link> · {c.subject_name}
                      {!c.is_graded && <span className="block text-xs text-muted">{t("subjects.nonGraded")}</span>}</Td>
                    <Td>{c.credits}</Td>
                    <Td className="text-right tabular-nums">{c.status === "FINALIZED" ? formatNumber(c.score_10, locale) : "—"}</Td>
                    <Td>{c.letter_grade ?? "—"}</Td>
                    <Td className="text-right tabular-nums">{c.grade_point !== null ? formatNumber(c.grade_point, locale, 1) : "—"}</Td>
                    <Td>
                      {c.status === "IN_PROGRESS" ? (
                        <span><Badge tone="info">{t("transcript.inProgress")}</Badge>
                          {c.provisional_score !== null && <span className="block text-xs text-muted">{t("transcript.provisional", {
                            score: formatNumber(c.provisional_score, locale), w: formatNumber(c.graded_weight, locale, 0) })}</span>}</span>
                      ) : c.is_passed ? <Badge tone="success">{t("transcript.pass")}</Badge> : <Badge tone="danger">{t("transcript.fail")}</Badge>}
                    </Td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </Card>
        ))}
      </div>
    </>
  );
}
