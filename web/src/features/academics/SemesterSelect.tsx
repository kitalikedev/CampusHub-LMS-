"use client";
import { Select } from "@/components/ui";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Semester } from "@/types/api";

export function SemesterSelect({ semesters, value, onChange, id, allowAll }: {
  semesters: Semester[]; value: number | null; onChange: (id: number | null) => void; id?: string; allowAll?: boolean;
}) {
  const t = useT();
  return (
    <Select id={id} value={value ?? ""} onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
            aria-label={t("semesters.label")} className="sm:w-72">
      {allowAll && <option value="">{t("common.all")}</option>}
      {semesters.map((s) => (
        <option key={s.id} value={s.id}>
          {s.code} · {s.name}{s.is_registration_open ? ` (${t("semesters.openShort")})` : ""}
        </option>
      ))}
    </Select>
  );
}

/** Học kỳ mặc định: đang mở đăng ký → đang diễn ra → mới nhất. */
export function defaultSemester(semesters: Semester[] | undefined, preferOpen = false): number | null {
  if (!semesters?.length) return null;
  const today = new Date().toISOString().slice(0, 10);
  const open = semesters.find((s) => s.is_registration_open);
  const current = semesters.find((s) => s.start_date <= today && today <= s.end_date);
  return (preferOpen ? open ?? current : current ?? open)?.id ?? semesters[0].id;
}
