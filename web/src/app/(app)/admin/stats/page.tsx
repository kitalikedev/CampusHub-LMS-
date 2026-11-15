"use client";
// SCR-A08 Thống kê (FR-STA-01, mức Could).
import { useState } from "react";

import { Card, EmptyState, ErrorState, PageHeader, SkeletonBlock, Stat, Table, Td, Th } from "@/components/ui";
import { SemesterSelect } from "@/features/academics";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Semester, Stats } from "@/types/api";

const LETTERS = ["A+", "A", "B+", "B", "C+", "C", "D+", "F"];

export default function StatsPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t, locale } = useI18n();
  const semesters = useApi<Semester[]>("/semesters");
  const [semesterId, setSemesterId] = useState<number | null>(null);
  const stats = useApi<Stats>(`/admin/stats${semesterId ? `?semester_id=${semesterId}` : ""}`);
  const totalLetters = stats.data ? Object.values(stats.data.letter_distribution).reduce((a, b) => a + b, 0) : 0;
  return (
    <>
      <PageHeader title={t("nav.stats")}
                  actions={semesters.data && <SemesterSelect semesters={semesters.data} value={semesterId} onChange={setSemesterId} allowAll />} />
      {stats.error && <ErrorState error={stats.error} onRetry={stats.reload} />}
      {!stats.data && !stats.error && <SkeletonBlock rows={6} />}
      {stats.data && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
            {(["STUDENT", "INSTRUCTOR", "ADMIN"] as const).map((r) => <Stat key={r} label={t(`roles.${r}`)} value={stats.data!.users_by_role[r] ?? 0} />)}
            <Stat label={t("stats.sections")} value={Object.values(stats.data.sections_by_status).reduce((a, b) => a + b, 0)} />
          </div>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card title={t("stats.letters")}>
              {totalLetters === 0 ? <EmptyState title={t("stats.noResults")} /> : (
                <ul className="space-y-2 text-sm">
                  {LETTERS.map((letter) => {
                    const n = stats.data!.letter_distribution[letter] ?? 0;
                    const pct = totalLetters ? (n / totalLetters) * 100 : 0;
                    return (
                      <li key={letter} className="grid grid-cols-[2.5rem_1fr_4rem] items-center gap-2">
                        <span className="font-medium">{letter}</span>
                        <span className="h-3 rounded bg-navy-50"><span className="block h-3 rounded bg-navy-700" style={{ width: `${pct}%` }} /></span>
                        <span className="text-right tabular-nums text-muted">{n}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </Card>
            <Card title={t("stats.passRates")}>
              {stats.data.pass_rates.length === 0 ? <EmptyState title={t("stats.noResults")} /> : (
                <Table>
                  <thead><tr><Th>{t("subjects.subject")}</Th><Th className="text-right">{t("stats.finalized")}</Th><Th className="text-right">{t("stats.passRate")}</Th></tr></thead>
                  <tbody className="divide-y divide-line">
                    {stats.data.pass_rates.map((r) => (
                      <tr key={r.subject_code}>
                        <Td>{r.subject_code} · {r.subject_name}</Td><Td className="text-right">{r.finalized}</Td>
                        <Td className="text-right tabular-nums">{formatNumber((r.passed / r.finalized) * 100, locale, 0)}%</Td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card>
          </div>
        </div>
      )}
    </>
  );
}
