"use client";
// Trang lịch dùng chung cho SV (thời khóa biểu) và GV (lịch dạy).
import { useState } from "react";

import { ErrorState, PageHeader, SkeletonBlock } from "@/components/ui";
import { defaultSemester, SemesterSelect } from "@/features/academics";
import { useApi } from "@/lib/api/useApi";
import { useT } from "@/lib/i18n/I18nProvider";
import type { ScheduleItem, Semester } from "@/types/api";

import { WeeklyTimetable } from "./WeeklyTimetable";

export function SchedulePage({ titleKey, linkBase }: { titleKey: string; linkBase: string }) {
  const t = useT();
  const semesters = useApi<Semester[]>("/semesters");
  const [picked, setPicked] = useState<number | null>(null);
  const semesterId = picked ?? defaultSemester(semesters.data);
  const schedule = useApi<{ items: ScheduleItem[] }>(semesterId ? `/me/schedule?semester_id=${semesterId}` : null);

  return (
    <>
      <PageHeader title={t(titleKey)} description={t("schedule.hint")}
                  actions={semesters.data && <SemesterSelect semesters={semesters.data} value={semesterId} onChange={setPicked} />} />
      {semesters.error && <ErrorState error={semesters.error} onRetry={semesters.reload} />}
      {schedule.error && <ErrorState error={schedule.error} onRetry={schedule.reload} />}
      {!schedule.data && !schedule.error && <SkeletonBlock rows={5} />}
      {schedule.data && <WeeklyTimetable items={schedule.data.items} linkBase={linkBase} />}
    </>
  );
}
