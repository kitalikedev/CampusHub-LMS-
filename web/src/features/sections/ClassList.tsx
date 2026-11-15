"use client";
// Danh sách lớp của tôi (SCR-S03) / lớp phụ trách (SCR-I02).
import Link from "next/link";

import { EmptyState, ErrorState, PageHeader, SkeletonBlock, Table, Td, Th } from "@/components/ui";
import { useApi } from "@/lib/api/useApi";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Section } from "@/types/api";

import { SectionStatusBadge, SlotList } from "./SectionBits";

export function ClassList({ base }: { base: string }) {
  const t = useT();
  const list = useApi<Section[]>("/me/sections");
  return (
    <>
      <PageHeader title={base.startsWith("/student") ? t("nav.myClasses") : t("nav.teachingClasses")} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock rows={5} />}
      {list.data?.length === 0 && <EmptyState title={t("dashboard.noClasses")} />}
      {list.data && list.data.length > 0 && (
        <Table>
          <thead><tr><Th>{t("semesters.label")}</Th><Th>{t("sections.code")}</Th><Th>{t("subjects.subject")}</Th>
            <Th>{t("sections.instructor")}</Th><Th>{t("sections.schedule")}</Th><Th>{t("common.status")}</Th></tr></thead>
          <tbody className="divide-y divide-line">
            {list.data.map((s) => (
              <tr key={s.id}>
                <Td>{s.semester.code}</Td>
                <Td><Link href={`${base}/${s.id}`} className="font-medium text-navy-700 hover:underline">{s.section_code}</Link></Td>
                <Td>{s.subject.code} · {s.subject.name}<span className="block text-xs text-muted">{t("common.creditsN", { n: s.subject.credits })}</span></Td>
                <Td>{s.instructor.full_name}</Td>
                <Td className="text-xs"><SlotList slots={s.slots} /></Td>
                <Td><SectionStatusBadge status={s.status} />{base.startsWith("/instructor") && <span className="block text-xs text-muted">{t("sections.enrolledN", { n: s.enrolled_count, cap: s.capacity })}</span>}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </>
  );
}
