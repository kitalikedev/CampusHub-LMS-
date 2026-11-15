"use client";
// SCR-C03 Tài khoản của tôi (FR-AUTH-03).
import { Card, DefinitionList, PageHeader, useToast } from "@/components/ui";
import { ChangePasswordForm } from "@/features/account";
import { useAuth } from "@/lib/auth/AuthProvider";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";

export default function AccountPage() {
  const { t, locale } = useI18n();
  const toast = useToast();
  const { user } = useAuth();
  if (!user) return null;
  return (
    <>
      <PageHeader title={t("nav.account")} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title={t("account.info")}>
          <DefinitionList items={[
            { label: t("users.fullName"), value: user.full_name },
            { label: t("users.email"), value: user.email },
            { label: t("users.role"), value: t(`roles.${user.role}`) },
            { label: t("users.studentCode"), value: user.student_code ?? "—" },
            { label: t("users.lastLogin"), value: formatDateTime(user.last_login_at, locale) },
          ]} />
        </Card>
        <Card title={t("account.changeTitle")}>
          <ChangePasswordForm onDone={() => toast(t("account.changed"))} />
        </Card>
      </div>
    </>
  );
}
