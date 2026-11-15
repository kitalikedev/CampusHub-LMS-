"use client";
// Toast thay cho alert() (NFR-USA-01).
import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";

type ToastTone = "success" | "danger" | "info";
interface ToastItem {
  id: number;
  tone: ToastTone;
  message: string;
}

const ToastContext = createContext<((message: string, tone?: ToastTone) => void) | null>(null);
const toneClass: Record<ToastTone, string> = {
  success: "border-success/30 text-success",
  danger: "border-danger/30 text-danger",
  info: "border-navy-200 text-ink",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const push = useCallback((message: string, tone: ToastTone = "success") => {
    const id = Date.now() + Math.random();
    setItems((list) => [...list, { id, tone, message }]);
    window.setTimeout(() => setItems((list) => list.filter((item) => item.id !== id)), 4500);
  }, []);
  const value = useMemo(() => push, [push]);
  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-4 bottom-4 z-[60] flex flex-col items-end gap-2 sm:left-auto sm:right-4 sm:w-96"
           aria-live="polite">
        {items.map((item) => (
          <div key={item.id} className={`pointer-events-auto w-full rounded-[var(--radius-control)] border bg-card px-4 py-3 text-sm shadow-md ${toneClass[item.tone]}`}>
            {item.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const push = useContext(ToastContext);
  if (!push) throw new Error("useToast must be used inside ToastProvider");
  return push;
}
