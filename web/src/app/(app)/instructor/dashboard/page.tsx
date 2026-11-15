"use client";
// SCR-I01 Tổng quan giảng viên (FR-DSH-02).
import Link from "next/link";

import { ButtonLink, Card, EmptyState, ErrorState, PageHeader, SkeletonBlock, Stat } from "@/components/ui";
import { SectionStatusBadge, sectionTitle, SlotList } from "@/features/sections";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Dashboard } from "@/types/api";

export default function InstructorDashboardPage() {
  return <RoleGate roles={["INSTRUCTOR"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const t = useT();
  const dash = useApi<Dashboard>("/me/dashboard");
  if (dash.error) return <ErrorState error={dash.error} onRetry={dash.reload} />;
  if (!dash.data) return <SkeletonBlock rows={6} />;
  const { semester, sections, pending_grading: pending, pending_regrades: regrades } = dash.data;
  return (
    <>
      <PageHeader title={t("dashboard.instructorTitle")} description={semester ? `${semester.code} · ${semester.name}` : undefined} />
      <div className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Stat label={t("dashboard.teaching")} value={sections.length} />
        <Stat label={t("dashboard.pendingGrading")} value={pending ?? 0} hint={t("dashboard.pendingGradingHint")} />
        <Stat label={t("dashboard.pendingRegrades")} value={regrades ?? 0} />
      </div>
      {(regrades ?? 0) > 0 && <div className="mb-4"><ButtonLink href="/instructor/regrades">{t("dashboard.goRegrades")}</ButtonLink></div>}
      <Card title={t("dashboard.teachingThisTerm")}>
        {sections.length === 0 ? <EmptyState title={t("dashboard.noClasses")} /> : (
          <ul className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {sections.map((s) => (
              <li key={s.id}>
                <Link href={`/instructor/classes/${s.id}`} className="block rounded-[var(--radius-control)] border border-line p-3 hover:border-navy-200">
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-ink">{sectionTitle(s)}</p>
                    <SectionStatusBadge status={s.status} />
                  </div>
                  <p className="text-xs text-muted">{t("sections.enrolledN", { n: s.enrolled_count, cap: s.capacity })}</p>
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
