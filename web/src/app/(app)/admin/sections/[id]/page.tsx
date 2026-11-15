"use client";
// SCR-A06 Chi tiết lớp (Admin): thông tin, lịch học (BR-ACD-05), công bố, xếp SV (BR-ENR-08), mở lại sổ (BR-LCK-06).
import { useParams } from "next/navigation";
import { FormEvent, useState } from "react";

import { Alert, Button, Card, ConfirmDialog, DefinitionList, ErrorState, Field, Input, PageHeader, Select, SkeletonBlock,
         Table, Td, Textarea, Th, useErrorText, useToast } from "@/components/ui";
import { SectionStatusBadge, sectionTitle } from "@/features/sections";
import { api, ApiError, toApiError } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { formatDateTime, formatTime } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Page, Room, RosterRow, Section, User } from "@/types/api";

export default function AdminSectionDetailPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const { t } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const { id } = useParams<{ id: string }>();
  const section = useApi<Section>(`/sections/${id}`);
  const [unlocking, setUnlocking] = useState(false);
  const [reason, setReason] = useState("");

  if (section.error) return <ErrorState error={section.error} onRetry={section.reload} />;
  if (!section.data) return <SkeletonBlock rows={6} />;
  const s = section.data;

  async function publish() {
    try {
      await api.post(`/sections/${s.id}/publish`);
      toast(t("sections.publishedToast"));
      section.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    }
  }

  async function unlock() {
    try {
      await api.post(`/sections/${s.id}/unlock`, { reason });
      toast(t("sections.unlocked"));
      setUnlocking(false);
      setReason("");
      section.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    }
  }

  return (
    <>
      <PageHeader title={sectionTitle(s)} description={<SectionStatusBadge status={s.status} />}
                  actions={<>
                    {s.status === "DRAFT" && <Button onClick={publish}>{t("sections.publish")}</Button>}
                    {s.status === "LOCKED" && <Button variant="danger" onClick={() => setUnlocking(true)}>{t("sections.unlock")}</Button>}
                  </>} />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <InfoCard section={s} onSaved={section.reload} />
        <SlotsCard section={s} onChanged={section.reload} />
      </div>
      <RosterCard section={s} onChanged={section.reload} />
      <ConfirmDialog open={unlocking} title={t("sections.unlockTitle")} message={t("sections.unlockText")}
                     confirmLabel={t("sections.unlock")} danger onConfirm={unlock} onClose={() => setUnlocking(false)}>
        <Field label={t("sections.reason")} required>
          {(p) => <Textarea {...p} required value={reason} onChange={(e) => setReason(e.target.value)} />}
        </Field>
      </ConfirmDialog>
    </>
  );
}

function InfoCard({ section, onSaved }: { section: Section; onSaved: () => void }) {
  const { t } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const instructors = useApi<Page<User>>("/admin/users?role=INSTRUCTOR&page_size=100");
  const [instructorId, setInstructorId] = useState(String(section.instructor.id));
  const [capacity, setCapacity] = useState(String(section.capacity));
  const [error, setError] = useState("");
  const locked = section.status === "LOCKED";

  async function save(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.patch(`/sections/${section.id}`, { instructor_id: Number(instructorId), capacity: Number(capacity) });
      toast(t("common.saved"));
      onSaved();
    } catch (err) {
      setError(errorText(err));
    }
  }

  return (
    <Card title={t("sections.info")}>
      <DefinitionList items={[
        { label: t("semesters.label"), value: `${section.semester.code} · ${section.semester.name}` },
        { label: t("subjects.credits"), value: section.subject.credits },
        { label: t("subjects.prerequisites"), value: section.prerequisites.map((p) => p.code).join(", ") || "—" },
        { label: t("sections.seats"), value: `${section.enrolled_count}/${section.capacity}` },
      ]} />
      <form onSubmit={save} className="mt-4 space-y-3 border-t border-line pt-4">
        {error && <Alert tone="danger">{error}</Alert>}
        <Field label={t("sections.instructor")}>
          {(p) => <Select {...p} disabled={locked} value={instructorId} onChange={(e) => setInstructorId(e.target.value)}>
            {instructors.data?.items.map((u) => <option key={u.id} value={u.id}>{u.full_name}</option>)}
            {!instructors.data && <option value={section.instructor.id}>{section.instructor.full_name}</option>}
          </Select>}
        </Field>
        <Field label={t("sections.capacity")}>
          {(p) => <Input {...p} type="number" min={1} disabled={locked} value={capacity} onChange={(e) => setCapacity(e.target.value)} />}
        </Field>
        {!locked && <Button type="submit" variant="secondary">{t("common.save")}</Button>}
      </form>
    </Card>
  );
}

function SlotsCard({ section, onChanged }: { section: Section; onChanged: () => void }) {
  const { t } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const rooms = useApi<Room[]>("/rooms");
  const [roomId, setRoomId] = useState("");
  const [day, setDay] = useState("2");
  const [start, setStart] = useState("08:00");
  const [end, setEnd] = useState("10:30");
  const [error, setError] = useState("");
  const locked = section.status === "LOCKED";

  async function add(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.post(`/sections/${section.id}/schedule-slots`, { room_id: Number(roomId), day_of_week: Number(day), start_time: start, end_time: end });
      toast(t("sections.slotAdded"));
      onChanged();
    } catch (err) {
      setError(errorText(err));
    }
  }

  async function remove(slotId: number) {
    try {
      await api.delete(`/schedule-slots/${slotId}`);
      onChanged();
    } catch (err) {
      toast(errorText(err), "danger");
    }
  }

  return (
    <Card title={t("sections.schedule")}>
      {section.slots.length === 0 ? <p className="text-sm text-muted">{t("sections.noSlots")}</p> : (
        <ul className="divide-y divide-line text-sm">
          {section.slots.map((slot) => (
            <li key={slot.id} className="flex items-center justify-between py-2">
              <span>{t(`days.${slot.day_of_week}`)} · {formatTime(slot.start_time)}–{formatTime(slot.end_time)} · {slot.room.code} ({slot.room.capacity})</span>
              {!locked && <Button size="sm" variant="ghost" onClick={() => remove(slot.id)}>{t("common.delete")}</Button>}
            </li>
          ))}
        </ul>
      )}
      {!locked && (
        <form onSubmit={add} className="mt-4 grid grid-cols-2 gap-3 border-t border-line pt-4">
          {error && <div className="col-span-2"><Alert tone="danger">{error}</Alert></div>}
          <Field label={t("schedule.room")} required>
            {(p) => <Select {...p} required value={roomId} onChange={(e) => setRoomId(e.target.value)}>
              <option value="">{t("common.choose")}</option>
              {rooms.data?.map((r) => <option key={r.id} value={r.id}>{r.code} ({r.capacity})</option>)}
            </Select>}
          </Field>
          <Field label={t("schedule.day")} required>
            {(p) => <Select {...p} value={day} onChange={(e) => setDay(e.target.value)}>
              {[1, 2, 3, 4, 5, 6, 7].map((d) => <option key={d} value={d}>{t(`days.${d}`)}</option>)}
            </Select>}
          </Field>
          <Field label={t("schedule.start")} required>{(p) => <Input {...p} type="time" required value={start} onChange={(e) => setStart(e.target.value)} />}</Field>
          <Field label={t("schedule.end")} required>{(p) => <Input {...p} type="time" required value={end} onChange={(e) => setEnd(e.target.value)} />}</Field>
          <div className="col-span-2"><Button type="submit" variant="secondary">{t("sections.addSlot")}</Button></div>
        </form>
      )}
    </Card>
  );
}

function RosterCard({ section, onChanged }: { section: Section; onChanged: () => void }) {
  const { t, locale } = useI18n();
  const toast = useToast();
  const errorText = useErrorText();
  const roster = useApi<RosterRow[]>(`/sections/${section.id}/enrollments`);
  const [q, setQ] = useState("");
  const students = useApi<Page<User>>(q.trim().length >= 2 ? `/admin/users?role=STUDENT&page_size=10&q=${encodeURIComponent(q.trim())}` : null);
  const [studentId, setStudentId] = useState("");
  const [violation, setViolation] = useState<ApiError | null>(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const locked = section.status === "LOCKED";

  async function add(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await api.post(`/sections/${section.id}/enrollments`, { student_id: Number(studentId), override_reason: violation ? reason : null });
      toast(t("sections.studentAdded"));
      setViolation(null);
      setReason("");
      setStudentId("");
      roster.reload();
      onChanged();
    } catch (err) {
      const apiError = toApiError(err);
      if (apiError.code === "ENROLLMENT_RULES_VIOLATED") setViolation(apiError);
      else setError(errorText(apiError));
    }
  }

  async function drop(studentIdToDrop: number) {
    try {
      await api.delete(`/sections/${section.id}/enrollments/${studentIdToDrop}`);
      roster.reload();
      onChanged();
    } catch (err) {
      toast(errorText(err), "danger");
    }
  }

  return (
    <Card title={t("sections.roster")} className="mt-4">
      {!locked && (
        <form onSubmit={add} className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
          {error && <div className="sm:col-span-3"><Alert tone="danger">{error}</Alert></div>}
          <Field label={t("sections.findStudent")} hint={t("sections.findHint")}>
            {(p) => <Input {...p} value={q} onChange={(e) => { setQ(e.target.value); setViolation(null); }} />}
          </Field>
          <Field label={t("sections.student")} required>
            {(p) => <Select {...p} required value={studentId} onChange={(e) => { setStudentId(e.target.value); setViolation(null); }}>
              <option value="">{t("common.choose")}</option>
              {students.data?.items.map((u) => <option key={u.id} value={u.id}>{u.student_code} · {u.full_name}</option>)}
            </Select>}
          </Field>
          <div className="flex items-end"><Button type="submit" variant="secondary">{t("sections.addStudent")}</Button></div>
          {violation && (
            <div className="space-y-3 sm:col-span-3">
              <Alert tone="warning" title={t("sections.violations")}>{errorText(violation)}</Alert>
              <Field label={t("sections.overrideReason")} required hint={t("sections.overrideHint")}>
                {(p) => <Textarea {...p} required value={reason} onChange={(e) => setReason(e.target.value)} />}
              </Field>
              <Button type="submit" variant="danger" disabled={!reason.trim()}>{t("sections.override")}</Button>
            </div>
          )}
        </form>
      )}
      {roster.error && <ErrorState error={roster.error} onRetry={roster.reload} />}
      {roster.data && roster.data.length === 0 && <p className="text-sm text-muted">{t("gradebook.noStudents")}</p>}
      {roster.data && roster.data.length > 0 && (
        <Table>
          <thead><tr><Th>{t("users.studentCode")}</Th><Th>{t("users.fullName")}</Th><Th>{t("users.email")}</Th><Th>{t("sections.enrolledAt")}</Th><Th /></tr></thead>
          <tbody className="divide-y divide-line">
            {roster.data.map((r) => (
              <tr key={r.enrollment_id}>
                <Td>{r.student.student_code}</Td><Td className="font-medium">{r.student.full_name}</Td><Td>{r.student.email}</Td>
                <Td>{formatDateTime(r.enrolled_at, locale)} · {t(`sections.source.${r.source}`)}</Td>
                <Td>{!locked && <Button size="sm" variant="ghost" onClick={() => drop(r.student.id)}>{t("sections.remove")}</Button>}</Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Card>
  );
}
