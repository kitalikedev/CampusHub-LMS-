"use client";
// SCR-C04 Thông báo hệ thống (FR-NOT-01).
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Badge, Button, EmptyState, ErrorState, PageHeader, SkeletonBlock, Tabs } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { AppNotification } from "@/types/api";

export default function NotificationsPage() {
  const { t, locale } = useI18n();
  const router = useRouter();
  const [tab, setTab] = useState<"unread" | "all">("unread");
  const list = useApi<{ items: AppNotification[]; unread_count: number }>(`/me/notifications${tab === "unread" ? "?unread=true" : ""}`);

  async function open(item: AppNotification) {
    if (!item.is_read) await api.post(`/me/notifications/${item.id}/read`);
    if (item.link) router.push(item.link);
    else list.reload();
  }

  async function readAll() {
    await api.post("/me/notifications/read-all");
    list.reload();
  }

  return (
    <>
      <PageHeader title={t("nav.notifications")}
                  actions={<Button variant="secondary" onClick={readAll} disabled={!list.data?.unread_count}>{t("notifications.readAll")}</Button>} />
      <Tabs value={tab} onChange={setTab} tabs={[{ id: "unread", label: t("notifications.unread") }, { id: "all", label: t("common.all") }]} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock />}
      {list.data?.items.length === 0 && <EmptyState title={t("notifications.empty")} />}
      <ul className="space-y-2">
        {list.data?.items.map((item) => (
          <li key={item.id}>
            <button type="button" onClick={() => open(item)}
                    className="w-full rounded-[var(--radius-card)] border border-line bg-card p-4 text-left hover:border-navy-200">
              <div className="flex items-start justify-between gap-2">
                <p className={`text-sm ${item.is_read ? "text-muted" : "font-medium text-ink"}`}>{t(`notifications.types.${item.type}`, item.params)}</p>
                {!item.is_read && <Badge tone="info">{t("notifications.new")}</Badge>}
              </div>
              <p className="mt-1 text-xs text-muted">{formatDateTime(item.created_at, locale)}</p>
            </button>
          </li>
        ))}
      </ul>
    </>
  );
}
