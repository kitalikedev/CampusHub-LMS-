"use client";
// SCR-A07 Nhật ký thao tác (FR-AUD-02; BR-AUD-01).
import { useState } from "react";

import { Button, EmptyState, ErrorState, PageHeader, Select, SkeletonBlock, Table, Td, Th } from "@/components/ui";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { AuditLog, Page } from "@/types/api";

const ACTIONS = ["USER_CREATED", "USERS_IMPORTED", "USER_UPDATED", "PASSWORD_RESET", "ENROLLMENT_ADDED_BY_ADMIN",
  "ENROLLMENT_DROPPED_BY_ADMIN", "GRADE_CHANGED", "GRADES_PUBLISHED", "SECTION_LOCKED", "SECTION_UNLOCKED", "REGRADE_RESOLVED"];
const PAGE_SIZE = 20;

export default function AuditLogsPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function short(value: unknown): string {
  if (value === null || value === undefined) return "";
  const text = JSON.stringify(value);
  return text.length > 120 ? `${text.slice(0, 117)}…` : text;
}

function Content() {
  const { t, locale } = useI18n();
  const [action, setAction] = useState("");
  const [page, setPage] = useState(1);
  const query = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
  if (action) query.set("action", action);
  const list = useApi<Page<AuditLog>>(`/admin/audit-logs?${query.toString()}`);
  const pages = list.data ? Math.max(1, Math.ceil(list.data.total / PAGE_SIZE)) : 1;
  return (
    <>
      <PageHeader title={t("nav.auditLogs")} description={t("audit.hint")}
                  actions={<Select aria-label={t("audit.action")} value={action} onChange={(e) => { setAction(e.target.value); setPage(1); }} className="sm:w-72">
                    <option value="">{t("common.all")}</option>
                    {ACTIONS.map((a) => <option key={a} value={a}>{t(`audit.actions.${a}`)}</option>)}
                  </Select>} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock rows={6} />}
      {list.data?.items.length === 0 && <EmptyState title={t("audit.empty")} />}
      {list.data && list.data.items.length > 0 && (
        <>
          <Table>
            <thead><tr><Th>{t("audit.time")}</Th><Th>{t("audit.action")}</Th><Th>{t("audit.actor")}</Th><Th>{t("audit.entity")}</Th>
              <Th>{t("audit.change")}</Th><Th>{t("sections.reason")}</Th></tr></thead>
            <tbody className="divide-y divide-line">
              {list.data.items.map((log) => (
                <tr key={log.id}>
                  <Td className="whitespace-nowrap">{formatDateTime(log.created_at, locale)}</Td>
                  <Td>{t(`audit.actions.${log.action}`)}</Td>
                  <Td>#{log.actor_id ?? "—"}</Td>
                  <Td>{log.entity_type} #{log.entity_id}</Td>
                  <Td className="font-mono text-xs">{short(log.before_data)}{log.before_data !== null && log.after_data !== null && " → "}{short(log.after_data)}</Td>
                  <Td>{log.reason ?? ""}</Td>
                </tr>
              ))}
            </tbody>
          </Table>
          <div className="mt-3 flex items-center justify-end gap-2 text-sm text-muted">
            <Button size="sm" variant="secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>{t("common.prev")}</Button>
            {t("common.pageOf", { page, pages })}
            <Button size="sm" variant="secondary" disabled={page >= pages} onClick={() => setPage(page + 1)}>{t("common.next")}</Button>
          </div>
        </>
      )}
    </>
  );
}
