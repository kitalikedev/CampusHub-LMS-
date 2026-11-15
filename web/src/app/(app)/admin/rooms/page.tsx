"use client";
// SCR-A05 Phòng học (FR-ACD-03; BR-ACD-06).
import { FormEvent, useState } from "react";

import { Alert, Button, ConfirmDialog, Dialog, EmptyState, ErrorState, Field, Input, PageHeader, SkeletonBlock, Table,
         Td, Th, useErrorText, useToast } from "@/components/ui";
import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { RoleGate } from "@/lib/auth/RoleGate";
import { useT } from "@/lib/i18n/I18nProvider";
import type { Room } from "@/types/api";

export default function RoomsPage() {
  return <RoleGate roles={["ADMIN"]}>{() => <Content />}</RoleGate>;
}

function Content() {
  const t = useT();
  const toast = useToast();
  const errorText = useErrorText();
  const list = useApi<Room[]>("/rooms");
  const [editing, setEditing] = useState<Room | "new" | null>(null);
  const [deleting, setDeleting] = useState<Room | null>(null);

  async function remove() {
    if (!deleting) return;
    try {
      await api.delete(`/rooms/${deleting.id}`);
      toast(t("common.deleted"));
      list.reload();
    } catch (err) {
      toast(errorText(err), "danger");
    }
    setDeleting(null);
  }

  return (
    <>
      <PageHeader title={t("nav.rooms")} actions={<Button onClick={() => setEditing("new")}>{t("rooms.create")}</Button>} />
      {list.error && <ErrorState error={list.error} onRetry={list.reload} />}
      {!list.data && !list.error && <SkeletonBlock />}
      {list.data?.length === 0 && <EmptyState title={t("rooms.empty")} />}
      {list.data && list.data.length > 0 && (
        <Table>
          <thead><tr><Th>{t("rooms.code")}</Th><Th>{t("rooms.name")}</Th><Th>{t("rooms.capacity")}</Th><Th className="w-48" /></tr></thead>
          <tbody className="divide-y divide-line">
            {list.data.map((r) => (
              <tr key={r.id}>
                <Td className="font-medium">{r.code}</Td><Td>{r.name}</Td><Td>{r.capacity}</Td>
                <Td><div className="flex gap-1">
                  <Button size="sm" variant="secondary" onClick={() => setEditing(r)}>{t("common.edit")}</Button>
                  <Button size="sm" variant="ghost" onClick={() => setDeleting(r)}>{t("common.delete")}</Button>
                </div></Td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      {editing && <RoomDialog room={editing === "new" ? undefined : editing} onClose={() => setEditing(null)}
                              onSaved={() => { setEditing(null); list.reload(); }} />}
      <ConfirmDialog open={deleting !== null} title={t("rooms.deleteTitle")} message={deleting?.code}
                     confirmLabel={t("common.delete")} danger onConfirm={remove} onClose={() => setDeleting(null)} />
    </>
  );
}

function RoomDialog({ room, onClose, onSaved }: { room?: Room; onClose: () => void; onSaved: () => void }) {
  const t = useT();
  const toast = useToast();
  const errorText = useErrorText();
  const [code, setCode] = useState(room?.code ?? "");
  const [name, setName] = useState(room?.name ?? "");
  const [capacity, setCapacity] = useState(String(room?.capacity ?? 40));
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      if (room) await api.patch(`/rooms/${room.id}`, { name, capacity: Number(capacity) });
      else await api.post("/rooms", { code, name, capacity: Number(capacity) });
      toast(t("common.saved"));
      onSaved();
    } catch (err) {
      setError(errorText(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open onClose={onClose} title={room ? t("rooms.edit") : t("rooms.create")}
            footer={<><Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button type="submit" form="room-form" loading={saving}>{t("common.save")}</Button></>}>
      <form id="room-form" onSubmit={submit} className="space-y-4">
        {error && <Alert tone="danger">{error}</Alert>}
        <Field label={t("rooms.code")} required>{(p) => <Input {...p} required disabled={Boolean(room)} value={code} onChange={(e) => setCode(e.target.value)} />}</Field>
        <Field label={t("rooms.name")} required>{(p) => <Input {...p} required value={name} onChange={(e) => setName(e.target.value)} />}</Field>
        <Field label={t("rooms.capacity")} required>{(p) => <Input {...p} type="number" min={1} required value={capacity} onChange={(e) => setCapacity(e.target.value)} />}</Field>
      </form>
    </Dialog>
  );
}
