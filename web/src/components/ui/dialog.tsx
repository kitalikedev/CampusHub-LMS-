"use client";
import { ReactNode, useEffect, useId } from "react";

import { Button } from "@/components/ui/button";
import { useT } from "@/lib/i18n/I18nProvider";

export function Dialog({ open, onClose, title, children, footer, wide }: {
  open: boolean; onClose: () => void; title: string; children: ReactNode; footer?: ReactNode; wide?: boolean;
}) {
  const id = useId();
  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-navy-900/40 p-0 sm:items-center sm:p-4"
         onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <div role="dialog" aria-modal="true" aria-labelledby={id}
           className={`max-h-[92vh] w-full overflow-y-auto rounded-t-[var(--radius-card)] bg-card shadow-lg sm:rounded-[var(--radius-card)] ${
             wide ? "sm:max-w-3xl" : "sm:max-w-lg"}`}>
        <div className="border-b border-line px-5 py-4">
          <h2 id={id} className="text-lg font-semibold text-ink">{title}</h2>
        </div>
        <div className="space-y-4 px-5 py-4">{children}</div>
        {footer && <div className="flex flex-wrap justify-end gap-2 border-t border-line px-5 py-3">{footer}</div>}
      </div>
    </div>
  );
}

export function ConfirmDialog({ open, title, message, confirmLabel, danger, loading, onConfirm, onClose, children }: {
  open: boolean; title: string; message: ReactNode; confirmLabel: string; danger?: boolean; loading?: boolean;
  onConfirm: () => void; onClose: () => void; children?: ReactNode;
}) {
  const t = useT();
  return (
    <Dialog open={open} onClose={onClose} title={title}
            footer={<>
              <Button variant="secondary" onClick={onClose}>{t("common.cancel")}</Button>
              <Button variant={danger ? "danger" : "primary"} loading={loading} onClick={onConfirm}>{confirmLabel}</Button>
            </>}>
      <div className="text-sm text-ink">{message}</div>
      {children}
    </Dialog>
  );
}
