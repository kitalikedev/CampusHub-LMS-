"use client";
// Khóa sổ theo checklist (FR-LCK-01, BR-LCK-01). Nút bị vô hiệu tới khi đủ điều kiện.
import { useState } from "react";

import { Alert, Button, Card, ConfirmDialog, ErrorState, SkeletonBlock, useErrorText, useToast } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { useT } from "@/lib/i18n/I18nProvider";
import type { LockCheck, SectionStatus } from "@/types/api";

export function LockPanel({ sectionId, status, onLocked }: { sectionId: number; status: SectionStatus; onLocked: () => void }) {
  const t = useT();
  const toast = useToast();
  const errorText = useErrorText();
  const check = useApi<LockCheck>(`/sections/${sectionId}/lock-check`);
  const [confirming, setConfirming] = useState(false);
  const [saving, setSaving] = useState(false);

  async function lock() {
    setSaving(true);
    try {
      await api.post(`/sections/${sectionId}/lock`);
      toast(t("lock.done"));
      setConfirming(false);
      check.reload();
      onLocked();
    } catch (err) {
      toast(errorText(err), "danger");
    } finally {
      setSaving(false);
    }
  }

  if (status === "LOCKED") return <Alert tone="info" title={t("lock.lockedTitle")}>{t("lock.lockedText")}</Alert>;
  if (check.error) return <ErrorState error={check.error} onRetry={check.reload} />;
  if (!check.data) return <SkeletonBlock />;
  return (
    <Card title={t("lock.title")}>
      <ul className="space-y-2 text-sm">
        {check.data.checks.map((c) => (
          <li key={c.key} className="flex items-start gap-2">
            <span className={`font-semibold ${c.ok ? "text-success" : "text-danger"}`}>{c.ok ? t("lock.ok") : t("lock.notOk")}</span>
            <span>{t(`lock.checks.${c.key}`)}{!c.ok && c.key !== "SECTION_PUBLISHED" && ` (${t(`lock.detail.${c.key}`, c.params as Record<string, number>)})`}</span>
          </li>
        ))}
      </ul>
      <p className="mt-4 text-sm text-muted">{t("lock.consequence")}</p>
      <div className="mt-4 flex gap-2">
        <Button onClick={() => setConfirming(true)} disabled={!check.data.can_lock}>{t("lock.action")}</Button>
        <Button variant="secondary" onClick={check.reload}>{t("lock.recheck")}</Button>
      </div>
      <ConfirmDialog open={confirming} title={t("lock.confirmTitle")} message={t("lock.consequence")}
                     confirmLabel={t("lock.action")} danger loading={saving} onConfirm={lock} onClose={() => setConfirming(false)} />
    </Card>
  );
}
