import { ReactNode, TdHTMLAttributes, ThHTMLAttributes } from "react";

export function PageHeader({ title, description, actions }: { title: string; description?: ReactNode; actions?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-col gap-3 border-b border-line pb-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h1 className="text-[1.75rem] font-semibold leading-tight sm:text-[2rem]">{title}</h1>
        {description && <div className="mt-1.5 text-[0.95rem] text-muted">{description}</div>}
      </div>
      {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
    </div>
  );
}

export function Card({ title, actions, children, className = "" }: {
  title?: string; actions?: ReactNode; children: ReactNode; className?: string;
}) {
  return (
    <section className={`rounded-[var(--radius-card)] border border-line bg-card p-4 sm:p-5 ${className}`}>
      {(title || actions) && (
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          {title && <h2 className="text-lg font-semibold">{title}</h2>}
          {actions && <div className="flex flex-wrap gap-2">{actions}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

export function Stat({ label, value, hint }: { label: string; value: ReactNode; hint?: string }) {
  return (
    <div className="rounded-[var(--radius-card)] border border-line border-t-[3px] border-t-navy-900 bg-card p-4">
      <p className="text-sm font-medium text-muted">{label}</p>
      <p className="mt-1 font-serif text-3xl font-semibold text-navy-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}

export function Tabs<T extends string>({ tabs, value, onChange }: {
  tabs: { id: T; label: string }[]; value: T; onChange: (id: T) => void;
}) {
  return (
    <div role="tablist" className="mb-5 flex gap-1 overflow-x-auto border-b border-line">
      {tabs.map((tab) => (
        <button key={tab.id} type="button" role="tab" aria-selected={tab.id === value}
                onClick={() => onChange(tab.id)}
                className={`-mb-px whitespace-nowrap border-b-[3px] px-3 py-2 text-[0.95rem] font-semibold transition-colors ${
                  tab.id === value ? "border-crimson-600 text-navy-900" : "border-transparent text-muted hover:text-navy-900"}`}>
          {tab.label}
        </button>
      ))}
    </div>
  );
}

/** Bảng cuộn ngang trong khung riêng (04 §2: không cuộn ngang cả trang). */
export function Table({ children }: { children: ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-[var(--radius-card)] border border-line bg-card">
      <table className="min-w-full divide-y divide-line text-sm">{children}</table>
    </div>
  );
}

export function Th({ className = "", ...props }: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th scope="col"
        className={`border-b-2 border-navy-900 bg-navy-50 px-3 py-2.5 text-left text-xs font-bold uppercase tracking-wide text-navy-900 ${className}`}
        {...props} />
  );
}

export function Td({ className = "", ...props }: TdHTMLAttributes<HTMLTableCellElement>) {
  return <td className={`px-3 py-2.5 align-top text-ink ${className}`} {...props} />;
}

export function DefinitionList({ items }: { items: { label: string; value: ReactNode }[] }) {
  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-3 text-sm sm:grid-cols-2">
      {items.map((item) => (
        <div key={item.label}>
          <dt className="text-xs font-semibold uppercase tracking-wide text-muted">{item.label}</dt>
          <dd className="mt-0.5 font-medium text-ink">{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}
