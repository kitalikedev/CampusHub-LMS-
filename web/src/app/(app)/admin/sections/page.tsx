"use client";
// SCR-A06 Lớp học phần (FR-ACD-04).
import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { Alert, Button, Dialog, EmptyState, ErrorState, Field, Input, PageHeader, Select, SkeletonBlock, Table, Td, Th,
         useErrorText } from "@/components/ui";
import { defaultSemester, SemesterSelect } from "@/features/academics";
import { SectionStatusBadge, SlotList } from "@/features/sections";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Page, Section, Semester, Subject, User } from "@/types/api";

export default function AdminSectionsPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const t = useT();
  const semesters = useApi<Semester[]>("/semesters");
  const [picked, setPicked] = useState<number | null>(null);
  const semesterId = picked ?? defaultSemester(semesters.data, true);
  const list = useApi<Section[]>(semesterId ? `/sections?semester_id=${semesterId}` : null);
  const [creating, setCreating] = useState(false);
  return (
    <>
      <PageHeader title={t("nav.sections")}
                  actions={<>
                    {semesters.data && <SemesterSelect semesters={semesters.data} value={semesterId} onChange={setPicked} />}
                    <Button onClick={() => setCreating(true)} disabled={!semesterId}>{t("sections.create")}</Button>
                  </>} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock rows={6} />}
      {list.data?.length === 0 && <EmptyState title={t("sections.empty")} />}
      {list.data && list.data.length > 0 && (
        <Table>
          <thead><tr><Th>{t("sections.code")}</Th><Th>{t("subjects.subject")}</Th><Th>{t("sections.instructor")}</Th>
            <Th>{t("sections.schedule")}</Th><Th>{t("sections.seats")}</Th><Th>{t("common.status")}</Th></tr></thead>
          <tbody className="divide-y divide-line">
            {list.data.map((s) => (
              <tr key={s.id}>
                <Td><Link href={`/admin/sections/${s.id}`} className="font-medium text-navy-700 hover:underline">{s.section_code}</Link></Td>
                <Td>{s.subject.code} · {s.subject.name}</Td>
                <Td>{s.instructor.full_name}</Td>
                <Td className="text-xs"><SlotList slots={s.slots} /></Td>
                <Td>{s.enrolled_count}/{s.capacity}</Td>
                <Td><SectionStatusBadge status={s.status} /></Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      {creating && semesterId && <CreateSectionDialog semesterId={semesterId} onClose={() => setCreating(false)} />}
    </>
  );
}

function CreateSectionDialog({ semesterId, onClose }: { semesterId: number; onClose: () => void }) {
  const t = useT();
  const router = useRouter();
  const errorText = useErrorText();
  const subjects = useApi<Subject[]>("/subjects");
  const instructors = useApi<Page<User>>("/admin/users?role=INSTRUCTOR&page_size=100");
  const [subjectId, setSubjectId] = useState("");
  const [instructorId, setInstructorId] = useState("");
  const [code, setCode] = useState("");
  const [capacity, setCapacity] = useState("40");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const r = await api.post<Section>("/sections", { semester_id: semesterId, subject_id: Number(subjectId),
        instructor_id: Number(instructorId), section_code: code, capacity: Number(capacity) });
      router.push(`/admin/sections/${r.data.id}`);
    } catch (err) {
      setError(errorText(err));
      setSaving(false);
    }
  }

  return (
    <Dialog open onClose={onClose} title={t("sections.create")}
            footer={<><Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button type="submit" form="section-form" loading={saving}>{t("common.create")}</Button></>}>
      <form id="section-form" onSubmit={submit} className="space-y-4">
        <Alert tone="info">{t("sections.draftHint")}</Alert>
        {error && <Alert tone="danger">{error}</Alert>}
        <Field label={t("subjects.subject")} required>
          {(p) => <Select {...p} required value={subjectId} onChange={(e) => setSubjectId(e.target.value)}>
            <option value="">{t("common.choose")}</option>
            {subjects.data?.map((s) => <option key={s.id} value={s.id}>{s.code} · {s.name} ({s.credits})</option>)}
          </Select>}
        </Field>
        <Field label={t("sections.instructor")} required>
          {(p) => <Select {...p} required value={instructorId} onChange={(e) => setInstructorId(e.target.value)}>
            <option value="">{t("common.choose")}</option>
            {instructors.data?.items.filter((u) => u.is_active).map((u) => <option key={u.id} value={u.id}>{u.full_name} · {u.email}</option>)}
          </Select>}
        </Field>
        <Field label={t("sections.code")} required hint={t("sections.codeHint")}>
          {(p) => <Input {...p} required maxLength={20} value={code} onChange={(e) => setCode(e.target.value)} />}
        </Field>
        <Field label={t("sections.capacity")} required>
          {(p) => <Input {...p} type="number" min={1} required value={capacity} onChange={(e) => setCapacity(e.target.value)} />}
        </Field>
      </form>
    </Dialog>
  );
}
