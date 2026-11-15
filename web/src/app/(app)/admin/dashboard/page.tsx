"use client";
// SCR-A01 Tổng quan Admin: lối tắt việc đầu kỳ + số liệu (FR-STA-01).
import { ButtonLink, Card, ErrorState, PageHeader, SkeletonBlock, Stat } from "@/components/ui";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Stats } from "@/types/api";

export default function AdminDashboardPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const t = useT();
  const stats = useApi<Stats>("/admin/stats");
  const steps = [
    { href: "/admin/semesters", key: "admin.step1" }, { href: "/admin/subjects", key: "admin.step2" },
    { href: "/admin/rooms", key: "admin.step3" }, { href: "/admin/sections", key: "admin.step4" },
    { href: "/admin/users", key: "admin.step5" },
  ];
  return (
    <>
      <PageHeader title={t("dashboard.adminTitle")} />
      {stats.error && <ErrorState error={stats.error} onRetry={stats.reload} />}
      {!stats.data && !stats.error && <SkeletonBlock />}
      {stats.data && (
        <div className="mb-6 grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Stat label={t("roles.STUDENT")} value={stats.data.users_by_role.STUDENT ?? 0} />
          <Stat label={t("roles.INSTRUCTOR")} value={stats.data.users_by_role.INSTRUCTOR ?? 0} />
          <Stat label={t("status.section.PUBLISHED")} value={stats.data.sections_by_status.PUBLISHED ?? 0} />
          <Stat label={t("status.section.LOCKED")} value={stats.data.sections_by_status.LOCKED ?? 0} />
        </div>
      )}
      <Card title={t("admin.startOfTerm")}>
        <ol className="space-y-2">
          {steps.map((step, index) => (
            <li key={step.href} className="flex flex-wrap items-center justify-between gap-2 rounded-[var(--radius-control)] border border-line p-3">
              <span className="text-sm"><span className="font-semibold">{index + 1}.</span> {t(step.key)}</span>
              <ButtonLink href={step.href} size="sm">{t("common.open")}</ButtonLink>
            </li>
          ))}
        </ol>
      </Card>
    </>
  );
}
