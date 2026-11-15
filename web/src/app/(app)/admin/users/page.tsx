"use client";
// SCR-A02 Người dùng (FR-USR-01…05).
import { useState } from "react";

import { Badge, Button, ConfirmDialog, EmptyState, ErrorState, Input, PageHeader, Select, SkeletonBlock, Table, Td, Th,
         useErrorText, useToast } from "@/components/ui";
import { Credential, ImportDialog, TempPasswordDialog, UserFormDialog } from "@/features/users";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Page, User, UserWithPassword } from "@/types/api";

const PAGE_SIZE = 20;

export default function UsersPage() {
  return <RoleGate roles={["ADMIN"]}>{(me) => <Content meId={me.id} />}</RoleGate>;
}

function Content({ meId }: { meId: number }) {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const [q, setQ] = useState("");
  const [role, setRole] = useState("");
  const [page, setPage] = useState(1);
  const query = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
  if (q.trim()) query.set("q", q.trim());
  if (role) query.set("role", role);
  const list = useApi<Page<User>>(`/admin/users?${query.toString()}`);
  const [editing, setEditing] = useState<User | "new" | null>(null);
  const [importing, setImporting] = useState(false);
  const [credentials, setCredentials] = useState<Credential[] | null>(null);
  const [resetting, setResetting] = useState<User | null>(null);
  const pages = list.data ? Math.max(1, Math.ceil(list.data.total / PAGE_SIZE)) : 1;

  async function reset() {
    if (!resetting) return;
    try {
      const r = await api.post<UserWithPassword>(`/admin/users/${resetting.id}/reset-password`);
      setCredentials([{ email: r.data.user.email, full_name: r.data.user.full_name, temp_password: r.data.temp_password }]);
      list.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    }
    setResetting(null);
  }

  async function toggleActive(user: User) {
    try {
      await api.patch(`/admin/users/${user.id}`, { is_active: !user.is_active });
      toast(user.is_active ? t("users.locked") : t("users.unlocked"));
      list.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    }
  }

  return (
    <>
      <PageHeader title={t("nav.users")} description={t("users.hint")}
                  actions={<>
                    <Button variant="secondary" onClick={() => setImporting(true)}>{t("users.import")}</Button>
                    <Button onClick={() => setEditing("new")}>{t("users.create")}</Button>
                  </>} />
      <div className="mb-4 flex flex-col gap-2 sm:flex-row">
        <Input placeholder={t("users.search")} aria-label={t("common.search")} value={q}
               onChange={(e) => { setQ(e.target.value); setPage(1); }} className="sm:max-w-sm" />
        <Select aria-label={t("users.role")} value={role} onChange={(e) => { setRole(e.target.value); setPage(1); }} className="sm:w-48">
          <option value="">{t("common.allRoles")}</option>
          {(["STUDENT", "INSTRUCTOR", "ADMIN"] as const).map((r) => <option key={r} value={r}>{t(`roles.${r}`)}</option>)}
        </Select>
      </div>
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock rows={6} />}
      {list.data?.items.length === 0 && <EmptyState title={t("users.empty")} />}
      {list.data && list.data.items.length > 0 && (
        <>
          <Table>
            <thead><tr><Th>{t("users.fullName")}</Th><Th>{t("users.email")}</Th><Th>{t("users.role")}</Th><Th>{t("common.status")}</Th>
              <Th>{t("users.lastLogin")}</Th><Th className="w-72">{t("common.actions")}</Th></tr></thead>
            <tbody className="divide-y divide-line">
              {list.data.items.map((u) => (
                <tr key={u.id}>
                  <Td className="font-medium">{u.full_name}{u.student_code && <span className="block text-xs text-muted">{u.student_code}</span>}</Td>
                  <Td>{u.email}</Td>
                  <Td>{t(`roles.${u.role}`)}</Td>
                  <Td className="space-x-1">
                    {u.is_active ? <Badge tone="success">{t("users.activeShort")}</Badge> : <Badge tone="danger">{t("users.lockedShort")}</Badge>}
                    {u.must_change_password && <Badge tone="warning">{t("users.mustChange")}</Badge>}
                  </Td>
                  <Td>{formatDateTime(u.last_login_at, locale)}</Td>
                  <Td>
                    <div className="flex flex-wrap gap-1">
                      <Button size="sm" variant="secondary" onClick={() => setEditing(u)}>{t("common.edit")}</Button>
                      <Button size="sm" variant="secondary" onClick={() => setResetting(u)}>{t("users.reset")}</Button>
                      {u.id !== meId && <Button size="sm" variant="ghost" onClick={() => toggleActive(u)}>{u.is_active ? t("users.lock") : t("users.unlock")}</Button>}
                    </div>
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
          <div className="mt-3 flex items-center justify-between text-sm text-muted">
            <span>{t("common.totalN", { n: list.data.total })}</span>
            <span className="flex items-center gap-2">
              <Button size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>{t("common.prev")}</Button>
              {t("common.pageOf", { page, pages })}
              <Button size="sm" variant="secondary" disabled={page >= pages} onClick={() => setPage(page + 1)}>{t("common.next")}</Button>
            </span>
          </div>
        </>
      )}
      {editing && (
        <UserFormDialog user={editing === "new" ? undefined : editing} onClose={() => setEditing(null)}
                        onCreated={(c) => { setEditing(null); setCredentials([c]); list.reload(); }}
                        onUpdated={() => { setEditing(null); list.reload(); }} />
      )}
      {importing && <ImportDialog onClose={() => setImporting(false)}
                                  onImported={(c) => { setImporting(false); setCredentials(c); list.reload(); }} />}
      {credentials && <TempPasswordDialog credentials={credentials} onClose={() => setCredentials(null)} />}
      <ConfirmDialog open={resetting !== null} title={t("users.resetTitle")} message={t("users.resetText", { email: resetting?.email ?? "" })}
                     confirmLabel={t("users.reset")} onConfirm={reset} onClose={() => setResetting(null)} />
    </>
  );
}
