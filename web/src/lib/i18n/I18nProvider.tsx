"use client";
// i18n tự viết (ADR-09): context + JSON, lựa chọn ngôn ngữ nhớ trong localStorage.
import { createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useSyncExternalStore } from "react";

import en from "@/lib/i18n/messages/en.json";
import vi from "@/lib/i18n/messages/vi.json";

export type Locale = "vi" | "en";
type Params = Record<string, string | number | null | undefined>;
type Messages = Record<string, unknown>;

const DICTS: Record<Locale, Messages> = { vi, en };
const KEY = "campushub.locale";
const EVENT = "campushub:locale";

const localeStore = {
  get(): Locale {
    try {
      return window.localStorage.getItem(KEY) === "en" ? "en" : "vi";
    } catch {
      return "vi";
    }
  },
  set(locale: Locale): void {
    try {
      window.localStorage.setItem(KEY, locale);
    } catch {
      /* bỏ qua */
    }
    window.dispatchEvent(new Event(EVENT));
  },
  subscribe(listener: () => void): () => void {
    window.addEventListener(EVENT, listener);
    window.addEventListener("storage", listener);
    return () => {
      window.removeEventListener(EVENT, listener);
      window.removeEventListener("storage", listener);
    };
  },
};

function lookup(dict: Messages, key: string): string | undefined {
  let node: unknown = dict;
  for (const part of key.split(".")) {
    if (node && typeof node === "object" && part in (node as Messages)) node = (node as Messages)[part];
    else return undefined;
  }
  return typeof node === "string" ? node : undefined;
}

export function interpolate(template: string, params?: Params): string {
  if (!params) return template;
  return template.replace(/\{(\w+)\}/g, (_, name: string) => {
    const value = params[name];
    return value === null || value === undefined ? "" : String(value);
  });
}

interface I18nValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, params?: Params) => string;
  has: (key: string) => boolean;
}

const I18nContext = createContext<I18nValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const locale = useSyncExternalStore(localeStore.subscribe, localeStore.get, () => "vi" as Locale);

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const t = useCallback(
    (key: string, params?: Params) => interpolate(lookup(DICTS[locale], key) ?? lookup(DICTS.vi, key) ?? key, params),
    [locale],
  );
  const has = useCallback((key: string) => lookup(DICTS[locale], key) !== undefined, [locale]);
  const value = useMemo(() => ({ locale, setLocale: localeStore.set, t, has }), [locale, t, has]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nValue {
  const value = useContext(I18nContext);
  if (!value) throw new Error("useI18n must be used inside I18nProvider");
  return value;
}

export function useT() {
  return useI18n().t;
}
