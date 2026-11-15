"use client";
// Thông báo lớp (FR-ANN-01, BR-ANN-01). GV phụ trách được đăng/xóa; SV của lớp chỉ xem.
import { FormEvent, useState } from "react";

import { Alert, Button, Card, ConfirmDialog, EmptyState, ErrorState, Field, Input, SkeletonBlock, Textarea,
         useErrorText, useToast } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { formatDateTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Announcement } from "@/types/api";

export function AnnouncementPanel({ sectionId, canManage }: { sectionId: number; canManage: boolean }) {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const list = useApi<Announcement[]>(`/sections/${sectionId}/announcements`);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<Announcement | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await api.post(`/sections/${sectionId}/announcements`, { title, content });
      setTitle("");
      setContent("");
      toast(t("announcements.posted"));
      list.reload();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  async function remove() {
    if (!deleting) return;
    try {
      await api.delete(`/announcements/${deleting.id}`);
      toast(t("common.deleted"));
      list.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    }
    setDeleting(null);
  }

  return (
    <div className="space-y-4">
      {canManage && (
        <Card title={t("announcements.new")}>
          <form onSubmit={submit} className="space-y-3">
            {error && <Alert tone="danger">{error}</Alert>}
            <Field label={t("announcements.title")} required>
              {(p) => <Input {...p} required maxLength={255} value={title} onChange={(e) => setTitle(e.target.value)} />}
            </Field>
            <Field label={t("announcements.content")} required>
              {(p) => <Textarea {...p} required rows={4} value={content} onChange={(e) => setContent(e.target.value)} />}
            </Field>
            <Button type="submit" loading={saving}>{t("announcements.post")}</Button>
          </form>
        </Card>
      )}
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock />}
      {list.data?.length === 0 && <EmptyState title={t("announcements.empty")} />}
      {list.data?.map((item) => (
        <Card key={item.id} title={item.title}
              actions={canManage && <Button variant="ghost" size="sm" onClick={() => setDeleting(item)}>{t("common.delete")}</Button>}>
          <p className="whitespace-pre-line text-sm text-ink">{item.content}</p>
          <p className="mt-3 text-xs text-muted">{item.author.full_name} · {formatDateTime(item.created_at, locale)}</p>
        </Card>
      ))}
      <ConfirmDialog open={deleting !== null} title={t("announcements.deleteTitle")} message={deleting?.title}
                     confirmLabel={t("common.delete")} danger onConfirm={remove} onClose={() => setDeleting(null)} />
    </div>
  );
}
