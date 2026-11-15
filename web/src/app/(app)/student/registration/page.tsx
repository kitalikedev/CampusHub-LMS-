"use client";
// SCR-S02 Đăng ký học phần (FR-ENR-01…03). Lý do bị chặn hiện ngay trên dòng.
import { useState } from "react";

import { Alert, Badge, Button, EmptyState, ErrorState, PageHeader, SkeletonBlock, Table, Td, Th, useErrorText,
         useToast } from "@/components/ui";
import { defaultSemester, SemesterSelect } from "@/features/academics";
import { SlotList } from "@/features/sections";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Section, Semester } from "@/types/api";

export default function RegistrationPage() {
  return <RoleGate roles={["STUDENT"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const semesters = useApi<Semester[]>("/semesters");
  const [picked, setPicked] = useState<number | null>(null);
  const semesterId = picked ?? defaultSemester(semesters.data, true);
  const sections = useApi<Section[]>(semesterId ? `/sections?semester_id=${semesterId}` : null);
  const [rowError, setRowError] = useState<Record<number, string>>({});
  const [busy, setBusy] = useState<number | null>(null);
  const [warning, setWarning] = useState("");
  const semester = semesters.data?.find((s) => s.id === semesterId);

  async function act(section: Section, enroll: boolean) {
    setBusy(section.id);
    setRowError((m) => ({ ...m, [section.id]: "" }));
    try {
      if (enroll) {
        const r = await api.post<{ warnings: string[] }>(`/sections/${section.id}/enrollments/self`);
        setWarning(r.data.warnings.includes("BELOW_MIN_CREDITS") ? t("registration.belowMin", { min: semester?.min_credits ?? 0 }) : "");
        toast(t("registration.enrolled", { code: section.section_code }));
      } else {
        await api.delete(`/sections/${section.id}/enrollments/self`);
        toast(t("registration.dropped", { code: section.section_code }));
      }
      sections.reload();
    } catch (err) {
      const message = errorText(err);
      setRowError((m) => ({ ...m, [section.id]: message }));
      toast(message, "danger");
    } finally {
      setBusy(null);
    }
  }

  const list = sections.data ?? [];
  const mine = list.filter((s) => s.is_enrolled);
  const registered = mine.reduce((sum, s) => sum + s.subject.credits, 0);

  return (
    <>
      <PageHeader title={t("registration.title")}
                  description={semester && t("registration.period", {
                    start: formatDateTime(semester.registration_start_at, locale),
                    end: formatDateTime(semester.registration_end_at, locale) })}
                  actions={semesters.data && <SemesterSelect semesters={semesters.data} value={semesterId} onChange={setPicked} />} />
      {semester && (
        <div className="mb-4 space-y-2">
          <Alert tone={semester.is_registration_open ? "info" : "warning"}>
            {semester.is_registration_open ? t("registration.open") : t("registration.closed")}
            {" · "}
            {t("registration.credits", { n: registered, max: semester.max_credits, min: semester.min_credits })}
          </Alert>
          {warning && <Alert tone="warning">{warning}</Alert>}
        </div>
      )}
      {semesters.error && <ErrorState error={semesters.error} onRetry={semesters.reload} />}
      {sections.error && <ErrorState error={sections.error} onRetry={sections.reload} />}
      {!sections.data && !sections.error && <SkeletonBlock rows={6} />}
      {sections.data && list.length === 0 && <EmptyState title={t("registration.empty")} />}
      {list.length > 0 && (
        <Table>
          <thead>
            <tr>
              <Th>{t("sections.code")}</Th><Th>{t("subjects.subject")}</Th><Th>{t("subjects.credits")}</Th>
              <Th>{t("sections.instructor")}</Th><Th>{t("sections.schedule")}</Th><Th>{t("sections.seats")}</Th>
              <Th>{t("subjects.prerequisites")}</Th><Th className="w-56">{t("common.actions")}</Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {list.map((s) => {
              const full = s.enrolled_count >= s.capacity;
              const canAct = s.registration_open && s.status === "PUBLISHED";
              return (
                <tr key={s.id}>
                  <Td className="font-medium">{s.section_code}</Td>
                  <Td>{s.subject.code}<span className="block text-xs text-muted">{s.subject.name}</span></Td>
                  <Td>{s.subject.credits}</Td>
                  <Td>{s.instructor.full_name}</Td>
                  <Td className="text-xs"><SlotList slots={s.slots} /></Td>
                  <Td className={full ? "text-danger" : ""}>{s.capacity - s.enrolled_count}/{s.capacity}</Td>
                  <Td className="text-xs">{s.prerequisites.map((p) => p.code).join(", ") || "—"}</Td>
                  <Td>
                    {s.is_enrolled ? (
                      <div className="space-y-1">
                        <Badge tone="success">{t("registration.registered")}</Badge>
                        {canAct && <Button size="sm" variant="secondary" loading={busy === s.id} onClick={() => act(s, false)}>{t("registration.drop")}</Button>}
                      </div>
                    ) : canAct ? (
                      <Button size="sm" loading={busy === s.id} onClick={() => act(s, true)}>{t("registration.enroll")}</Button>
                    ) : <span className="text-xs text-muted">{t("registration.notOpen")}</span>}
                    {rowError[s.id] && <p className="mt-1 text-xs text-danger" role="alert">{rowError[s.id]}</p>}
                  </Td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      )}
    </>
  );
}
