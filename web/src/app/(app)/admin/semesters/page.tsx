"use client";
// SCR-A03 Học kỳ và đợt đăng ký (FR-ACD-01; BR-ACD-01).
import { FormEvent, useState } from "react";

import { Alert, Badge, Button, Dialog, EmptyState, ErrorState, Field, Input, PageHeader, SkeletonBlock, Table, Td, Th,
         useErrorText, useToast } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDate, formatDateTime, fromLocalInput, toLocalInput } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Semester } from "@/types/api";

export default function SemestersPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t, locale } = useI18n();
  const list = useApi<Semester[]>("/semesters");
  const [editing, setEditing] = useState<Semester | "new" | null>(null);
  return (
    <>
      <PageHeader title={t("nav.semesters")} actions={<Button onClick={() => setEditing("new")}>{t("semesters.create")}</Button>} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock />}
      {list.data?.length === 0 && <EmptyState title={t("semesters.empty")} />}
      {list.data && list.data.length > 0 && (
        <Table>
          <thead><tr><Th>{t("semesters.code")}</Th><Th>{t("semesters.name")}</Th><Th>{t("semesters.dates")}</Th>
            <Th>{t("semesters.registration")}</Th><Th>{t("semesters.creditLimits")}</Th><Th /></tr></thead>
          <tbody className="divide-y divide-line">
            {list.data.map((s) => (
              <tr key={s.id}>
                <Td className="font-medium">{s.code}</Td><Td>{s.name}</Td>
                <Td>{formatDate(s.start_date, locale)} – {formatDate(s.end_date, locale)}</Td>
                <Td>{formatDateTime(s.registration_start_at, locale)} – {formatDateTime(s.registration_end_at, locale)}
                  {s.is_registration_open && <span className="ml-1"><Badge tone="success">{t("semesters.openShort")}</Badge></span>}</Td>
                <Td>{s.min_credits} – {s.max_credits}</Td>
                <Td><Button size="sm" variant="secondary" onClick={() => setEditing(s)}>{t("common.edit")}</Button></Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      {editing && <SemesterDialog semester={editing === "new" ? undefined : editing} onClose={() => setEditing(null)}
                                  onSaved={() => { setEditing(null); list.reload(); }} />}
    </>
  );
}

function SemesterDialog({ semester, onClose, onSaved }: { semester?: Semester; onClose: () => void; onSaved: () => void }) {
  const t = useI18n().t;
  const toast = useToast();
  const errorText = useErrorText();
  const [form, setForm] = useState({
    code: semester?.code ?? "", name: semester?.name ?? "", start_date: semester?.start_date ?? "", end_date: semester?.end_date ?? "",
    reg_start: toLocalInput(semester?.registration_start_at), reg_end: toLocalInput(semester?.registration_end_at),
    min_credits: String(semester?.min_credits ?? 12), max_credits: String(semester?.max_credits ?? 24),
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const set = (key: keyof typeof form) => (e: { target: { value: string } }) => setForm({ ...form, [key]: e.target.value });

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const body = {
      name: form.name, start_date: form.start_date, end_date: form.end_date,
      registration_start_at: fromLocalInput(form.reg_start), registration_end_at: fromLocalInput(form.reg_end),
      min_credits: Number(form.min_credits), max_credits: Number(form.max_credits),
    };
    try {
      if (semester) await api.patch(`/semesters/${semester.id}`, body);
      else await api.post("/semesters", { ...body, code: form.code });
      toast(t("common.saved"));
      onSaved();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open onClose={onClose} title={semester ? t("semesters.edit") : t("semesters.create")} wide
            footer={<><Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button type="submit" form="semester-form" loading={saving}>{t("common.save")}</Button></>}>
      <form id="semester-form" onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {error && <div className="sm:col-span-2"><Alert tone="danger">{error}</Alert></div>}
        <Field label={t("semesters.code")} required hint={t("semesters.codeHint")}>
          {(p) => <Input {...p} required disabled={Boolean(semester)} value={form.code} onChange={set("code")} />}
        </Field>
        <Field label={t("semesters.name")} required>{(p) => <Input {...p} required value={form.name} onChange={set("name")} />}</Field>
        <Field label={t("semesters.start")} required>{(p) => <Input {...p} type="date" required value={form.start_date} onChange={set("start_date")} />}</Field>
        <Field label={t("semesters.end")} required>{(p) => <Input {...p} type="date" required value={form.end_date} onChange={set("end_date")} />}</Field>
        <Field label={t("semesters.regStart")} required>{(p) => <Input {...p} type="datetime-local" required value={form.reg_start} onChange={set("reg_start")} />}</Field>
        <Field label={t("semesters.regEnd")} required>{(p) => <Input {...p} type="datetime-local" required value={form.reg_end} onChange={set("reg_end")} />}</Field>
        <Field label={t("semesters.minCredits")} required>{(p) => <Input {...p} type="number" min={0} max={60} required value={form.min_credits} onChange={set("min_credits")} />}</Field>
        <Field label={t("semesters.maxCredits")} required>{(p) => <Input {...p} type="number" min={1} max={60} required value={form.max_credits} onChange={set("max_credits")} />}</Field>
      </form>
    </Dialog>
  );
}
