// Dịch lỗi API theo mã (ADR-08), xử lý các tham số đặc biệt.
import type { ApiError } from "@/lib/api/client";

type T = (key: string, params?: Record<string, string | number | null | undefined>) => string;

function flatParams(params: Record<string, unknown>, t: T): Record<string, string | number> {
  const out: Record<string, string | number> = {};
  for (const [key, value] of Object.entries(params)) {
    if (key === "day" && typeof value === "number") out.day = t(`days.${value}`);
    else if (Array.isArray(value) && value.every((v) => typeof v === "string")) out[key] = value.join(", ");
    else if (typeof value === "string" || typeof value === "number") out[key] = value;
  }
  return out;
}

export function errorMessage(error: ApiError | undefined, t: T, has: (key: string) => boolean): string {
  if (!error) return "";
  const params = flatParams(error.params, t);
  if (error.code === "ENROLLMENT_RULES_VIOLATED" && Array.isArray(error.params.violations)) {
    const items = (error.params.violations as { code: string; params: Record<string, unknown> }[])
      .map((v) => errorMessage({ code: v.code, params: v.params || {}, status: 409 }, t, has));
    return `${t("errors.ENROLLMENT_RULES_VIOLATED")} ${items.join(" · ")}`;
  }
  if (error.code === "LOCK_PRECONDITION_FAILED" && Array.isArray(error.params.failed)) {
    const items = (error.params.failed as { key: string }[]).map((c) => t(`lock.checks.${c.key}`));
    return `${t("errors.LOCK_PRECONDITION_FAILED")} ${items.join(" · ")}`;
  }
  if (typeof error.params.reason === "string") {
    const reasonKey = `errors.reasons.${error.params.reason}`;
    if (has(reasonKey)) return t(reasonKey, params);
  }
  if (error.code === "IMPORT_INVALID_ROWS" && Array.isArray(error.params.rows)) {
    const rows = (error.params.rows as { row: number; code: string; email?: string }[])
      .slice(0, 5).map((r) => t("users.importRowError", { row: r.row, email: r.email ?? "", code: t(`users.importCodes.${r.code}`) }));
    return `${t("errors.IMPORT_INVALID_ROWS")} ${rows.join(" · ")}`;
  }
  const key = `errors.${error.code}`;
  return has(key) ? t(key, params) : t("errors.UNKNOWN", { code: error.code });
}
