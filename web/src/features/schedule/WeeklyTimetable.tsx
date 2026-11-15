"use client";
// Lịch tuần Thứ Hai–Chủ nhật (SCR-S06, SCR-I06). Giờ học hiển thị nguyên văn, không quy đổi múi giờ.
import Link from "next/link";

import { EmptyState } from "@/components/ui";
import { formatTime } from "@/lib/format";
import { useT } from "@/lib/i18n/I18nProvider";
import type { ScheduleItem } from "@/types/api";

export function WeeklyTimetable({ items, linkBase }: { items: ScheduleItem[]; linkBase: string }) {
  const t = useT();
  if (!items.length) return <EmptyState title={t("schedule.empty")} />;
  const days = [1, 2, 3, 4, 5, 6, 7];
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-7">
      {days.map((day) => {
        const slots = items.filter((i) => i.day_of_week === day);
        return (
          <section key={day} className="rounded-[var(--radius-card)] border border-line bg-card p-3">
            <h3 className="mb-2 text-sm font-semibold text-ink">{t(`days.${day}`)}</h3>
            {slots.length === 0 && <p className="text-xs text-muted">{t("schedule.noClass")}</p>}
            <ul className="space-y-2">
              {slots.map((slot) => (
                <li key={`${slot.section_id}-${slot.start_time}`}>
                  <Link href={`${linkBase}/${slot.section_id}`}
                        className="block rounded-[var(--radius-control)] border border-navy-100 bg-navy-50 p-2 text-xs hover:border-navy-200">
                    <p className="font-semibold text-ink">{formatTime(slot.start_time)}–{formatTime(slot.end_time)}</p>
                    <p className="mt-0.5 text-ink">{slot.subject_code} · {slot.section_code}</p>
                    <p className="text-muted">{slot.subject_name}</p>
                    <p className="text-muted">{t("schedule.room")}: {slot.room_code}</p>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        );
      })}
    </div>
  );
}
