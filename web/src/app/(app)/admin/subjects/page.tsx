"use client";
// SCR-A04 Môn học và môn tiên quyết (FR-ACD-02; BR-ACD-02).
import { FormEvent, useState } from "react";

import { Alert, Badge, Button, Checkbox, Dialog, EmptyState, ErrorState, Field, Input, PageHeader, SkeletonBlock, Table,
         Td, Textarea, Th, useErrorText, useToast } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Subject } from "@/types/api";

export default function SubjectsPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const t = useT();
  const list = useApi<Subject[]>("/subjects");
  const [editing, setEditing] = useState<Subject | "new" | null>(null);
  return (
    <>
      <PageHeader title={t("nav.subjects")} actions={<Button onClick={() => setEditing("new")}>{t("subjects.create")}</Button>} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock />}
      {list.data?.length === 0 && <EmptyState title={t("subjects.empty")} />}
      {list.data && list.data.length > 0 && (
        <Table>
          <thead><tr><Th>{t("subjects.code")}</Th><Th>{t("subjects.name")}</Th><Th>{t("subjects.credits")}</Th>
            <Th>{t("subjects.type")}</Th><Th>{t("subjects.prerequisites")}</Th><Th /></tr></thead>
          <tbody className="divide-y divide-line">
            {list.data.map((s) => (
              <tr key={s.id}>
                <Td className="font-medium">{s.code}</Td><Td>{s.name}</Td><Td>{s.credits}</Td>
                <Td>{s.is_graded ? t("subjects.graded") : <Badge tone="outline">{t("subjects.nonGraded")}</Badge>}</Td>
                <Td>{s.prerequisites.map((p) => p.code).join(", ") || "—"}</Td>
                <Td><Button size="sm" variant="secondary" onClick={() => setEditing(s)}>{t("common.edit")}</Button></Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      {editing && list.data && (
        <SubjectDialog subject={editing === "new" ? undefined : editing} all={list.data} onClose={() => setEditing(null)}
                       onSaved={() => { setEditing(null); list.reload(); }} />
      )}
    </>
  );
}

function SubjectDialog({ subject, all, onClose, onSaved }: { subject?: Subject; all: Subject[]; onClose: () => void; onSaved: () => void }) {
  const t = useT();
  const toast = useToast();
  const errorText = useErrorText();
  const [code, setCode] = useState(subject?.code ?? "");
  const [name, setName] = useState(subject?.name ?? "");
  const [credits, setCredits] = useState(String(subject?.credits ?? 3));
  const [graded, setGraded] = useState(subject?.is_graded ?? true);
  const [description, setDescription] = useState(subject?.description ?? "");
  const [prereqs, setPrereqs] = useState<number[]>(subject?.prerequisites.map((p) => p.id) ?? []);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const body = { name, credits: Number(credits), is_graded: graded, description: description || null };
    try {
      const saved = subject
        ? (await api.patch<Subject>(`/subjects/${subject.id}`, body)).data
        : (await api.post<Subject>("/subjects", { ...body, code })).data;
      await api.put(`/subjects/${saved.id}/prerequisites`, { prerequisite_ids: prereqs });
      toast(t("common.saved"));
      onSaved();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open onClose={onClose} title={subject ? t("subjects.edit") : t("subjects.create")} wide
            footer={<><Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button type="submit" form="subject-form" loading={saving}>{t("common.save")}</Button></>}>
      <form id="subject-form" onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {error && <div className="sm:col-span-2"><Alert tone="danger">{error}</Alert></div>}
        <Field label={t("subjects.code")} required>{(p) => <Input {...p} required disabled={Boolean(subject)} value={code} onChange={(e) => setCode(e.target.value)} />}</Field>
        <Field label={t("subjects.name")} required>{(p) => <Input {...p} required value={name} onChange={(e) => setName(e.target.value)} />}</Field>
        <Field label={t("subjects.credits")} required>{(p) => <Input {...p} type="number" min={1} max={10} required value={credits} onChange={(e) => setCredits(e.target.value)} />}</Field>
        <div className="flex items-end pb-2"><Checkbox label={t("subjects.nonGradedLabel")} checked={!graded} onChange={(e) => setGraded(!e.target.checked)} /></div>
        <div className="sm:col-span-2"><Field label={t("subjects.description")}>{(p) => <Textarea {...p} value={description} onChange={(e) => setDescription(e.target.value)} />}</Field></div>
        <fieldset className="sm:col-span-2">
          <legend className="mb-2 text-sm font-medium text-ink">{t("subjects.prerequisites")}</legend>
          <div className="grid max-h-48 grid-cols-1 gap-1 overflow-y-auto rounded-[var(--radius-control)] border border-line p-3 sm:grid-cols-2">
            {all.filter((s) => s.id !== subject?.id).map((s) => (
              <Checkbox key={s.id} label={`${s.code} · ${s.name}`} checked={prereqs.includes(s.id)}
                        onChange={(e) => setPrereqs(e.target.checked ? [...prereqs, s.id] : prereqs.filter((id) => id !== s.id))} />
            ))}
          </div>
        </fieldset>
      </form>
    </Dialog>
  );
}
