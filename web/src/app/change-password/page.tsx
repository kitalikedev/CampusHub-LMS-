"use client";
// SCR-C02 Đổi mật khẩu bắt buộc ở lần đăng nhập đầu (BR-ACC-04).
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Alert, Button, SkeletonBlock } from "@/components/ui";
import { ChangePasswordForm } from "@/features/account";
import { homeFor, useAuth } from "@/lib/auth/AuthProvider";
import { useT } from "@/lib/i18n/I18nProvider";

export default function ChangePasswordPage() {
  const t = useT();
  const router = useRouter();
  const { status, user, refresh, logout } = useAuth();

  useEffect(() => {
    if (status === "anonymous") router.replace("/login");
    else if (user && !user.must_change_password) router.replace(homeFor(user.role)); // đã đổi xong
  }, [status, user, router]);

  if (!user || !user.must_change_password) {
    return <div className="mx-auto max-w-md px-6 py-24"><SkeletonBlock rows={3} /></div>;
  }
  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-12">
      <div className="w-full max-w-md space-y-4 rounded-[var(--radius-card)] border border-line bg-card p-6 shadow-sm">
        <h1 className="text-xl font-semibold text-ink">{t("account.forcedTitle")}</h1>
        <Alert tone="info">{t("account.forcedText", { email: user.email })}</Alert>
        <ChangePasswordForm onDone={refresh} />
        <Button variant="ghost" size="sm" onClick={logout}>{t("nav.logout")}</Button>
      </div>
    </div>
  );
}
