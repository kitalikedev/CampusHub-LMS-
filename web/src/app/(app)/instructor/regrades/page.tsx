"use client";
// SCR-I05 Xử lý phúc khảo (FR-REG-02; BR-REG-03).
import Link from "next/link";
import { useState } from "react";

import { Alert, Badge, Button, Card, EmptyState, ErrorState, Field, Input, PageHeader, SkeletonBlock, Tabs, Textarea,
         useErrorText, useToast } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime, formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { RegradeView } from "@/types/api";

export default function RegradesPage() {
  return <RoleGate roles={["INSTRUCTOR"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t } = useI18n();
  const [tab, setTab] = useState<"PENDING" | "ALL">("PENDING");
  const list = useApi<RegradeView[]>(tab === "PENDING" ? "/regrade-requests?status=PENDING" : "/regrade-requests");
  return (
    <>
      <PageHeader title={t("nav.regrades")} description={t("regrades.hint")} />
      <Tabs value={tab} onChange={setTab} tabs={[{ id: "PENDING", label: t("status.regrade.PENDING") }, { id: "ALL", label: t("common.all") }]} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock />}
      {list.data?.length === 0 && <EmptyState title={t("regrades.empty")} />}
      <div className="space-y-3">
        {list.data?.map((item) => <RegradeCard key={item.request.id} item={item} onDone={list.reload} />)}
      </div>
    </>
  );
}

function RegradeCard({ item, onDone }: { item: RegradeView; onDone: () => void }) {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const [score, setScore] = useState(String(item.current_score));
  const [response, setResponse] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const r = item.request;

  async function resolve(accept: boolean) {
    setSaving(true);
    setError("");
    try {
      await api.post(`/regrade-requests/${r.id}/resolve`, { accept, new_score: accept ? Number(score) : null, response });
      toast(t("regrades.resolved"));
      onDone();
    } catch (err) {
      setError(errorText(err));
      setSaving(false);
    }
  }

  return (
    <Card title={`${item.assignment_title} · ${item.section_code}`}
          actions={<Badge tone={r.status === "PENDING" ? "warning" : r.status === "ACCEPTED" ? "success" : "neutral"}>{t(`status.regrade.${r.status}`)}</Badge>}>
      <p className="text-sm"><span className="font-medium">{item.student.full_name}</span> ({item.student.student_code}) · {formatDateTime(r.created_at, locale)}</p>
      <p className="mt-1 text-sm text-muted">{t("regrades.oldScore")}: {formatNumber(r.old_score, locale)}
        {r.new_score !== null && ` → ${formatNumber(r.new_score, locale)}`}</p>
      <p className="mt-2 whitespace-pre-line rounded-[var(--radius-control)] bg-surface p-3 text-sm">{r.reason}</p>
      {r.response && <p className="mt-2 text-sm text-muted">{t("regrades.response")}: {r.response}</p>}
      {r.status === "PENDING" && (
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
          {error && <div className="sm:col-span-3"><Alert tone="danger">{error}</Alert></div>}
          <Field label={t("regrades.newScore")}>
            {(p) => <Input {...p} type="number" min={0} max={10} step={0.01} value={score} onChange={(e) => setScore(e.target.value)} />}
          </Field>
          <div className="sm:col-span-2">
            <Field label={t("regrades.response")} hint={t("regrades.responseHint")}>
              {(p) => <Textarea {...p} rows={2} value={response} onChange={(e) => setResponse(e.target.value)} />}
            </Field>
          </div>
          <div className="flex gap-2 sm:col-span-3">
            <Button loading={saving} onClick={() => resolve(true)}>{t("regrades.accept")}</Button>
            <Button variant="secondary" loading={saving} onClick={() => resolve(false)}>{t("regrades.reject")}</Button>
            <Link href={`/instructor/assignments/${item.assignment_id}`} className="ml-auto self-center text-sm text-navy-700 hover:underline">{t("grading.open")}</Link>
          </div>
        </div>
      )}
    </Card>
  );
}
