"use client";
// Tạo/sửa bài tập – cột điểm (FR-ASG-01, 02; BR-ASG-01…08).
import { FormEvent, useState } from "react";

import { Alert, Button, Dialog, Field, Input, Select, Textarea, useErrorText, useToast } from "@/components/ui";
import { api } from "@/lib/api/client";
import { fromLocalInput, toLocalInput } from "@/lib/format";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Assignment, GradeVisibility, LatePolicy, SubmissionMode } from "@/types/api";

interface Props {
  sectionId: number;
  assignment?: Assignment; // có: sửa; không: tạo mới
  weightUsed: number; // tổng trọng số các bài khác
  onClose: () => void;
  onSaved: () => void;
}

export function AssignmentForm({ sectionId, assignment, weightUsed, onClose, onSaved }: Props) {
  const t = useT();
  const toast = useToast();
  const errorText = useErrorText();
  const [title, setTitle] = useState(assignment?.title ?? "");
  const [description, setDescription] = useState(assignment?.description ?? "");
  const [weight, setWeight] = useState(String(assignment?.weight_percent ?? Math.max(0, 100 - weightUsed)));
  const [mode, setMode] = useState<SubmissionMode>(assignment?.submission_mode ?? "SINGLE");
  const [attempts, setAttempts] = useState(String(assignment?.max_attempts ?? 3));
  const [due, setDue] = useState(toLocalInput(assignment?.due_at));
  const [late, setLate] = useState<LatePolicy>(assignment?.late_policy ?? "REJECT");
  const [visibility, setVisibility] = useState<GradeVisibility>(assignment?.grade_visibility ?? "IMMEDIATE");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const offline = mode === "OFFLINE";
  const remaining = Math.round((100 - weightUsed) * 100) / 100;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setSaving(true);
    const body = {
      title, description: description || null, weight_percent: Number(weight), submission_mode: mode,
      max_attempts: mode === "MULTIPLE" ? Number(attempts) : null,
      due_at: offline ? null : fromLocalInput(due), late_policy: offline ? null : late, grade_visibility: visibility,
    };
    try {
      if (assignment) await api.patch(`/assignments/${assignment.id}`, body);
      else await api.post(`/sections/${sectionId}/assignments`, body);
      toast(t("common.saved"));
      onSaved();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open onClose={onClose} title={assignment ? t("assignments.edit") : t("assignments.create")} wide
            footer={<>
              <Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button type="submit" form="assignment-form" loading={saving}>{t("common.save")}</Button>
            </>}>
      <form id="assignment-form" onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {error && <div className="sm:col-span-2"><Alert tone="danger">{error}</Alert></div>}
        <div className="sm:col-span-2">
          <Field label={t("assignments.title")} required>
            {(p) => <Input {...p} required maxLength={255} value={title} onChange={(e) => setTitle(e.target.value)} />}
          </Field>
        </div>
        <div className="sm:col-span-2">
          <Field label={t("assignments.description")}>
            {(p) => <Textarea {...p} value={description} onChange={(e) => setDescription(e.target.value)} />}
          </Field>
        </div>
        <Field label={t("assignments.weight")} required hint={t("assignments.weightHint", { remaining })}>
          {(p) => <Input {...p} type="number" required min={0.01} max={100} step={0.01} value={weight}
                         onChange={(e) => setWeight(e.target.value)} />}
        </Field>
        <Field label={t("assignments.mode")} required hint={t(`modesHint.${mode}`)}>
          {(p) => (
            <Select {...p} value={mode} onChange={(e) => setMode(e.target.value as SubmissionMode)}>
              {(["SINGLE", "OVERWRITE", "MULTIPLE", "OFFLINE"] as const).map((m) => <option key={m} value={m}>{t(`modes.${m}`)}</option>)}
            </Select>
          )}
        </Field>
        {mode === "MULTIPLE" && (
          <Field label={t("assignments.maxAttempts")} required>
            {(p) => <Input {...p} type="number" required min={1} max={20} value={attempts}
                           onChange={(e) => setAttempts(e.target.value)} />}
          </Field>
        )}
        {!offline && (
          <>
            <Field label={t("assignments.dueLocal")} required>
              {(p) => <Input {...p} type="datetime-local" required value={due} onChange={(e) => setDue(e.target.value)} />}
            </Field>
            <Field label={t("assignments.latePolicy")} required>
              {(p) => (
                <Select {...p} value={late} onChange={(e) => setLate(e.target.value as LatePolicy)}>
                  <option value="REJECT">{t("late.REJECT")}</option>
                  <option value="ACCEPT_MARK_LATE">{t("late.ACCEPT_MARK_LATE")}</option>
                </Select>
              )}
            </Field>
          </>
        )}
        <Field label={t("assignments.visibility")} required hint={t(`visibilityHint.${visibility}`)}>
          {(p) => (
            <Select {...p} value={visibility} onChange={(e) => setVisibility(e.target.value as GradeVisibility)}>
              <option value="IMMEDIATE">{t("visibility.IMMEDIATE")}</option>
              <option value="MANUAL">{t("visibility.MANUAL")}</option>
            </Select>
          )}
        </Field>
      </form>
    </Dialog>
  );
}
