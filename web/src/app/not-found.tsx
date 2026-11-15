"use client";
// SCR-C05 Không tìm thấy trang.
import { ButtonLink } from "@/components/ui";
import { useT } from "@/lib/i18n/I18nProvider";

export default function NotFound() {
  const t = useT();
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 px-4 text-center">
      <p className="text-lg font-semibold text-ink">{t("common.notFoundTitle")}</p>
      <p className="text-sm text-muted">{t("common.notFoundText")}</p>
      <ButtonLink href="/" variant="primary">{t("common.home")}</ButtonLink>
    </div>
  );
}
