"use client";
// Đổi mật khẩu (FR-AUTH-02, 03; BR-ACC-05).
import { FormEvent, useState } from "react";

import { Alert, Button, Field, Input, useErrorText } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useT } from "@/lib/i18n/I18nProvider";

export function ChangePasswordForm({ onDone }: { onDone: () => void }) {
  const t = useT();
  const errorText = useErrorText();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    if (next !== confirm) {
      setError(t("account.mismatch"));
      return;
    }
    setSaving(true);
    try {
      await api.post("/auth/change-password", { current_password: current, new_password: next });
      setCurrent("");
      setNext("");
      setConfirm("");
      onDone();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      {error && <Alert tone="danger">{error}</Alert>}
      <Field label={t("account.current")} required>
        {(p) => <Input {...p} type="password" autoComplete="current-password" required value={current}
                       onChange={(e) => setCurrent(e.target.value)} />}
      </Field>
      <Field label={t("account.new")} hint={t("account.rule")} required>
        {(p) => <Input {...p} type="password" autoComplete="new-password" required minLength={8} value={next}
                       onChange={(e) => setNext(e.target.value)} />}
      </Field>
      <Field label={t("account.confirm")} required>
        {(p) => <Input {...p} type="password" autoComplete="new-password" required value={confirm}
                       onChange={(e) => setConfirm(e.target.value)} />}
      </Field>
      <Button type="submit" loading={saving}>{t("account.submit")}</Button>
    </form>
  );
}
