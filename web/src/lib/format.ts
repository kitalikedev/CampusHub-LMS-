// Định dạng ngày giờ theo giờ Việt Nam và số theo ngôn ngữ (04 §7, BR-GEN-01).
import type { Locale } from "@/lib/i18n/I18nProvider";

const TZ = "Asia/Ho_Chi_Minh";
const tag = (locale: Locale) => (locale === "vi" ? "vi-VN" : "en-GB");

export function formatDateTime(value: string | null | undefined, locale: Locale): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat(tag(locale), {
    timeZone: TZ, day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit",
  }).format(new Date(value));
}

export function formatDate(value: string | null | undefined, locale: Locale): string {
  if (!value) return "—";
  // Ngày thuần (YYYY-MM-DD) không quy đổi múi giờ.
  const date = value.length === 10 ? new Date(`${value}T00:00:00Z`) : new Date(value);
  return new Intl.DateTimeFormat(tag(locale), {
    timeZone: value.length === 10 ? "UTC" : TZ, day: "2-digit", month: "2-digit", year: "numeric",
  }).format(date);
}

export function formatNumber(value: number | null | undefined, locale: Locale, digits = 2): string {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat(tag(locale), { minimumFractionDigits: digits, maximumFractionDigits: digits })
    .format(value);
}

/** Giờ học "08:00:00" → "08:00" (giờ địa phương, không quy đổi). */
export function formatTime(value: string): string {
  return value.slice(0, 5);
}

/** Giá trị cho <input type="datetime-local"> theo giờ Việt Nam. */
export function toLocalInput(value: string | null | undefined): string {
  if (!value) return "";
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date(value));
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? "00";
  return `${get("year")}-${get("month")}-${get("day")}T${get("hour")}:${get("minute")}`;
}

/** Giá trị nhập theo giờ Việt Nam (UTC+7) → ISO UTC kèm "Z". */
export function fromLocalInput(value: string): string | null {
  if (!value) return null;
  return new Date(`${value}:00+07:00`).toISOString();
}

export function formatBytes(size: number): string {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}
