"use client";
// Tạo/sửa tài khoản, hiện mật khẩu tạm một lần, import CSV (FR-USR-01…05; BR-ACC-01…10).
import { FormEvent, useState } from "react";

import { Alert, Button, Checkbox, Dialog, Field, Input, Select, Table, Td, Textarea, Th, useErrorText,
         useToast } from "@/components/ui";
import { api, saveBlob } from "@/lib/api/client";
import { useT } from "@/lib/i18n/I18nProvider";
import type { ImportedAccount, Role, User, UserWithPassword } from "@/types/api";

export interface Credential {
  email: string;
  full_name: string;
  temp_password: string;
}

function credentialsCsv(list: Credential[]): Blob {
  const lines = ["email,full_name,temp_password", ...list.map((c) => `${c.email},"${c.full_name.replace(/"/g, '""')}",${c.temp_password}`)];
  return new Blob([`﻿${lines.join("\n")}`], { type: "text/csv;charset=utf-8" });
}

/** Mật khẩu tạm chỉ hiện đúng một lần (AC-USR-01.1). */
export function TempPasswordDialog({ credentials, onClose }: { credentials: Credential[]; onClose: () => void }) {
  const t = useT();
  const toast = useToast();
  const text = credentials.map((c) => `${c.email}\t${c.temp_password}`).join("\n");
  return (
    <Dialog open onClose={onClose} title={t("users.tempTitle")} wide
            footer={<>
              <Button variant="secondary" onClick={() => saveBlob(credentialsCsv(credentials), "campushub-accounts.csv")}>{t("users.downloadCsv")}</Button>
              <Button variant="secondary" onClick={() => navigator.clipboard?.writeText(text).then(() => toast(t("users.copied")))}>{t("users.copy")}</Button>
              <Button onClick={onClose}>{t("users.savedIt")}</Button>
            </>}>
      <Alert tone="warning">{t("users.tempWarning")}</Alert>
      <Table>
        <thead><tr><Th>{t("users.email")}</Th><Th>{t("users.fullName")}</Th><Th>{t("users.tempPassword")}</Th></tr></thead>
        <tbody className="divide-y divide-line">
          {credentials.map((c) => (
            <tr key={c.email}><Td>{c.email}</Td><Td>{c.full_name}</Td><Td className="font-mono text-base">{c.temp_password}</Td></tr>
          ))}
        </tbody>
      </Table>
    </Dialog>
  );
}

export function UserFormDialog({ user, onClose, onCreated, onUpdated }: {
  user?: User; onClose: () => void; onCreated: (c: Credential) => void; onUpdated: () => void;
}) {
  const t = useT();
  const toast = useToast();
  const errorText = useErrorText();
  const [email, setEmail] = useState(user?.email ?? "");
  const [name, setName] = useState(user?.full_name ?? "");
  const [role, setRole] = useState<Role>(user?.role ?? "STUDENT");
  const [code, setCode] = useState(user?.student_code ?? "");
  const [active, setActive] = useState(user?.is_active ?? true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (user) {
        await api.patch(`/admin/users/${user.id}`, { full_name: name, role, student_code: role === "STUDENT" ? code : null, is_active: active });
        toast(t("common.saved"));
        onUpdated();
      } else {
        const r = await api.post<UserWithPassword>("/admin/users", { email, full_name: name, role, student_code: role === "STUDENT" ? code : null });
        onCreated({ email: r.data.user.email, full_name: r.data.user.full_name, temp_password: r.data.temp_password });
      }
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open onClose={onClose} title={user ? t("users.edit") : t("users.create")}
            footer={<>
              <Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button type="submit" form="user-form" loading={saving}>{t("common.save")}</Button>
            </>}>
      <form id="user-form" onSubmit={submit} className="space-y-4">
        {error && <Alert tone="danger">{error}</Alert>}
        <Field label={t("users.email")} required hint={t("users.emailHint")}>
          {(p) => <Input {...p} type="email" required disabled={Boolean(user)} value={email} onChange={(e) => setEmail(e.target.value)} />}
        </Field>
        <Field label={t("users.fullName")} required>
          {(p) => <Input {...p} required value={name} onChange={(e) => setName(e.target.value)} />}
        </Field>
        <Field label={t("users.role")} required>
          {(p) => (
            <Select {...p} value={role} onChange={(e) => setRole(e.target.value as Role)}>
              {(["STUDENT", "INSTRUCTOR", "ADMIN"] as const).map((r) => <option key={r} value={r}>{t(`roles.${r}`)}</option>)}
            </Select>
          )}
        </Field>
        {role === "STUDENT" && (
          <Field label={t("users.studentCode")} required>
            {(p) => <Input {...p} required maxLength={20} value={code} onChange={(e) => setCode(e.target.value)} />}
          </Field>
        )}
        {user && <Checkbox label={t("users.active")} checked={active} onChange={(e) => setActive(e.target.checked)} />}
        {!user && <p className="text-xs text-muted">{t("users.tempHint")}</p>}
      </form>
    </Dialog>
  );
}

export function ImportDialog({ onClose, onImported }: { onClose: () => void; onImported: (c: Credential[]) => void }) {
  const t = useT();
  const errorText = useErrorText();
  const [csv, setCsv] = useState("email,full_name,role,student_code\n");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function readFile(file: File | undefined) {
    if (file) setCsv(await file.text());
  }

  async function submit() {
    setSaving(true);
    setError("");
    try {
      const r = await api.post<{ created: ImportedAccount[] }>("/admin/users/import", { csv_text: csv });
      onImported(r.data.created);
    } catch (err) {
      setError(errorText(err));
      setSaving(false);
    }
  }

  return (
    <Dialog open onClose={onClose} title={t("users.import")} wide
            footer={<>
              <Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button loading={saving} onClick={submit}>{t("users.importAction")}</Button>
            </>}>
      <Alert tone="info">{t("users.importHint")}</Alert>
      {error && <Alert tone="danger">{error}</Alert>}
      <Field label={t("users.importFile")}>
        {(p) => <Input {...p} type="file" accept=".csv,text/csv" onChange={(e) => readFile(e.target.files?.[0])} />}
      </Field>
      <Field label={t("users.importContent")}>
        {(p) => <Textarea {...p} rows={8} className="font-mono text-xs" value={csv} onChange={(e) => setCsv(e.target.value)} />}
      </Field>
    </Dialog>
  );
}
