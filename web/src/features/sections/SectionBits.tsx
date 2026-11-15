"use client";
import { Badge, Tone } from "@/components/ui";
import { formatTime } from "@/lib/format";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Section, SectionStatus, Slot } from "@/types/api";

const statusTone: Record<SectionStatus, Tone> = { DRAFT: "outline", PUBLISHED: "info", LOCKED: "danger" };

export function SectionStatusBadge({ status }: { status: SectionStatus }) {
  const t = useT();
  return <Badge tone={statusTone[status]}>{t(`status.section.${status}`)}</Badge>;
}

export function SlotList({ slots, withRoom = true }: { slots: Slot[]; withRoom?: boolean }) {
  const t = useT();
  if (!slots.length) return <span className="text-muted">{t("sections.noSlots")}</span>;
  return (
    <ul className="space-y-0.5">
      {slots.map((s) => (
        <li key={s.id}>
          {t(`daysShort.${s.day_of_week}`)} {formatTime(s.start_time)}–{formatTime(s.end_time)}
          {withRoom && <span className="text-muted"> · {s.room.code}</span>}
        </li>
      ))}
    </ul>
  );
}

export function sectionTitle(section: Pick<Section, "section_code" | "subject">): string {
  return `${section.subject.code} · ${section.subject.name} (${section.section_code})`;
}
