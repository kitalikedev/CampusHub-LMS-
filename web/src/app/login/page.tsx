"use client";
// SCR-C01 Đăng nhập bằng email (FR-AUTH-01). Không có đăng ký công khai (BR-ACC-01).
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { LanguageSwitch, Wordmark } from "@/components/layout/AppShell";
import { Alert, Button, Field, Input, useErrorText } from "@/components/ui";
import { homeFor, useAuth } from "@/lib/auth/AuthProvider";
import { useT } from "@/lib/i18n/I18nProvider";

export default function LoginPage() {
  const t = useT();
  const errorText = useErrorText();
  const router = useRouter();
  const { login, status, user } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (status === "authenticated" && user) {
      router.replace(user.must_change_password ? "/change-password" : homeFor(user.role));
    }
  }, [status, user, router]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(errorText(err));
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <div className="h-1 bg-crimson-600" aria-hidden />
      <div className="flex min-h-[calc(100vh-4px)] items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-end justify-between">
          <div>
            <h1 className="sr-only">CampusHub</h1>
            <Wordmark subtitle={t("app.tagline")} />
            <p className="mt-3 text-sm text-muted">{t("login.subtitle")}</p>
          </div>
          <LanguageSwitch />
        </div>
        <form onSubmit={submit} className="space-y-4 rounded-[var(--radius-card)] border border-line border-t-[3px] border-t-navy-900 bg-card p-6">
          {error && <Alert tone="danger">{error}</Alert>}
          <Field label={t("login.email")} required>
            {(p) => <Input {...p} type="email" autoComplete="username" required value={email}
                           onChange={(e) => setEmail(e.target.value)} />}
          </Field>
          <Field label={t("login.password")} required>
            {(p) => <Input {...p} type="password" autoComplete="current-password" required value={password}
                           onChange={(e) => setPassword(e.target.value)} />}
          </Field>
          <Button type="submit" className="w-full" loading={loading}>{t("login.submit")}</Button>
          <p className="text-xs text-muted">{t("login.noSignup")}</p>
        </form>
      </div>
      </div>
    </div>
  );
}
