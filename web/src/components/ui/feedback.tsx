"use client";
import { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import type { ApiError } from "@/lib/api/client";
import { useErrorText } from "@/components/ui/useErrorText";
import { useT } from "@/lib/i18n/I18nProvider";

export type Tone = "neutral" | "info" | "success" | "warning" | "danger" | "outline";

const tones: Record<Tone, string> = {
  neutral: "bg-surface text-muted border-line",
  info: "bg-info-soft text-info border-navy-100",
  success: "bg-success-soft text-success border-transparent",
  warning: "bg-warning-soft text-warning border-transparent",
  danger: "bg-danger-soft text-danger border-transparent",
  outline: "bg-card text-muted border-line",
};

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>
      {children}
    </span>
  );
}

export function Alert({ tone = "info", title, children }: { tone?: Tone; title?: string; children?: ReactNode }) {
  return (
    <div role={tone === "danger" ? "alert" : "status"}
         className={`rounded-[var(--radius-control)] border px-4 py-3 text-sm ${tones[tone]}`}>
      {title && <p className="font-semibold">{title}</p>}
      {children && <div className={title ? "mt-1" : ""}>{children}</div>}
    </div>
  );
}

export function Skeleton({ className = "h-4 w-full" }: { className?: string }) {
  return <div className={`animate-pulse rounded bg-navy-50 ${className}`} aria-hidden />;
}

export function SkeletonBlock({ rows = 4 }: { rows?: number }) {
  const t = useT();
  return (
    <div className="space-y-3" role="status" aria-label={t("common.loading")}>
      {Array.from({ length: rows }, (_, i) => <Skeleton key={i} className={i === 0 ? "h-6 w-1/3" : "h-4 w-full"} />)}
    </div>
  );
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="rounded-[var(--radius-card)] border border-dashed border-line bg-card px-6 py-10 text-center">
      <p className="font-medium text-ink">{title}</p>
      {description && <p className="mt-1 text-sm text-muted">{description}</p>}
      {action && <div className="mt-4 flex justify-center">{action}</div>}
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: ApiError; onRetry?: () => void }) {
  const t = useT();
  const text = useErrorText();
  if (error.status === 403) return <Forbidden />;
  return (
    <div className="rounded-[var(--radius-card)] border border-line bg-card px-6 py-8 text-center" role="alert">
      <p className="font-medium text-danger">{text(error)}</p>
      {onRetry && <Button variant="secondary" className="mt-4" onClick={onRetry}>{t("common.retry")}</Button>}
    </div>
  );
}

export function Forbidden() {
  const t = useT();
  return (
    <div className="rounded-[var(--radius-card)] border border-line bg-card px-6 py-10 text-center" role="alert">
      <p className="text-lg font-semibold text-ink">{t("common.forbiddenTitle")}</p>
      <p className="mt-1 text-sm text-muted">{t("common.forbiddenText")}</p>
    </div>
  );
}
