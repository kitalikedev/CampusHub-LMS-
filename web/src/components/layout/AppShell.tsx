"use client";
// Bố cục chung (04 §2), hướng "Học thuật cổ điển": header trắng có vạch đỏ VNUK, sidebar trắng,
// breadcrumb, skip link (WCAG 2.1 AA). Tham khảo nguyên tắc USWDS/Stanford/Harvard/U-M.
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode, useEffect, useState } from "react";

import { Button } from "@/components/ui";
import { NAVIGATION, NavItem } from "@/config/navigation";
import { useApi } from "@/lib/api/useApi";
import { useAuth } from "@/lib/auth/AuthProvider";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { User } from "@/types/api";

function LanguageSwitch() {
  const { locale, setLocale, t } = useI18n();
  return (
    <div className="flex overflow-hidden rounded-[var(--radius-control)] border border-navy-900 text-xs" role="group"
         aria-label={t("common.language")}>
      {(["vi", "en"] as const).map((code) => (
        <button key={code} type="button" onClick={() => setLocale(code)} aria-pressed={locale === code}
                className={`px-2.5 py-1.5 font-semibold ${locale === code ? "bg-navy-900 text-white" : "bg-card text-navy-900 hover:bg-navy-50"}`}>
          {code.toUpperCase()}
        </button>
      ))}
    </div>
  );
}

function Wordmark({ subtitle }: { subtitle?: string }) {
  return (
    <span className="flex flex-col leading-tight">
      <span className="font-serif text-xl font-semibold text-navy-900">
        Campus<span className="text-crimson-600">Hub</span>
      </span>
      {subtitle && <span className="text-xs font-medium text-muted">{subtitle}</span>}
    </span>
  );
}

function NotificationLink() {
  const { t } = useI18n();
  const { data, reload } = useApi<{ unread_count: number }>("/me/notifications?unread=true");
  useEffect(() => {
    const timer = window.setInterval(reload, 60_000); // ADR-11: polling 60 giây
    return () => window.clearInterval(timer);
  }, [reload]);
  const count = data?.unread_count ?? 0;
  return (
    <Link href="/notifications" className="rounded-[var(--radius-control)] px-2.5 py-1.5 text-sm font-semibold text-navy-900 hover:bg-navy-50">
      {t("nav.notifications")}
      {count > 0 && (
        <span className="ml-1.5 rounded-full bg-crimson-600 px-1.5 py-0.5 text-xs font-bold text-white"
              aria-label={t("nav.unreadCount", { n: count })}>{count}</span>
      )}
    </Link>
  );
}

function activeItem(items: NavItem[], pathname: string): NavItem | undefined {
  return items.find((item) => pathname === item.href || pathname.startsWith(`${item.href}/`));
}

function Sidebar({ user, onNavigate }: { user: User; onNavigate?: () => void }) {
  const pathname = usePathname();
  const { t } = useI18n();
  const current = activeItem(NAVIGATION[user.role], pathname);
  return (
    <nav aria-label={t("nav.main")}>
      <p className="px-3 pb-2 text-xs font-bold uppercase tracking-wider text-muted">{t(`roles.${user.role}`)}</p>
      <ul className="space-y-0.5">
        {NAVIGATION[user.role].map((item) => {
          const active = item === current;
          return (
            <li key={item.href}>
              <Link href={item.href} onClick={onNavigate} aria-current={active ? "page" : undefined}
                    className={`block border-l-[3px] px-3 py-2 text-[0.95rem] ${
                      active ? "border-crimson-600 bg-navy-50 font-semibold text-navy-900"
                        : "border-transparent text-ink hover:border-navy-200 hover:bg-navy-50 hover:text-navy-900"}`}>
                {t(item.labelKey)}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

/** Breadcrumb tự suy từ menu (USWDS: giữ trải nghiệm liền mạch, người dùng biết mình đang ở đâu). */
function Breadcrumb({ user }: { user: User }) {
  const pathname = usePathname();
  const { t } = useI18n();
  const items = NAVIGATION[user.role];
  const home = items[0];
  const current = activeItem(items, pathname);
  const crumbs: { label: string; href?: string }[] = [{ label: t(home.labelKey), href: home.href }];
  if (current && current !== home) crumbs.push({ label: t(current.labelKey), href: current.href });
  if (current && pathname !== current.href) crumbs.push({ label: t("nav.detail") });
  if (!current && pathname !== home.href) {
    const extra = pathname.startsWith("/notifications") ? "nav.notifications" : pathname.startsWith("/account") ? "nav.account" : null;
    if (extra) crumbs.push({ label: t(extra) });
  }
  if (crumbs.length < 2) return null;
  return (
    <nav aria-label={t("nav.breadcrumb")} className="mb-3 text-sm">
      <ol className="flex flex-wrap items-center gap-1.5 text-muted">
        {crumbs.map((crumb, index) => (
          <li key={`${crumb.label}-${index}`} className="flex items-center gap-1.5">
            {index > 0 && <span aria-hidden>›</span>}
            {crumb.href && index < crumbs.length - 1
              ? <Link href={crumb.href} className="text-navy-700 underline hover:text-navy-900">{crumb.label}</Link>
              : <span aria-current="page" className="text-ink">{crumb.label}</span>}
          </li>
        ))}
      </ol>
    </nav>
  );
}

export function AppShell({ user, children }: { user: User; children: ReactNode }) {
  const { t } = useI18n();
  const { logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <div className="min-h-screen">
      <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded focus:bg-card focus:px-3 focus:py-2 focus:text-navy-900 focus:shadow">
        {t("nav.skip")}
      </a>
      <div className="h-1 bg-crimson-600" aria-hidden />
      <header className="sticky top-0 z-30 border-b border-line bg-card">
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <Button variant="secondary" size="sm" className="md:hidden" onClick={() => setMenuOpen(true)}>{t("nav.menu")}</Button>
            <Link href={NAVIGATION[user.role][0].href} aria-label="CampusHub"><Wordmark subtitle={t("app.tagline")} /></Link>
          </div>
          <div className="flex flex-wrap items-center gap-1 sm:gap-2">
            <span className="hidden text-right text-sm leading-tight lg:block">
              <span className="block font-semibold text-ink">{user.full_name}</span>
              <span className="block text-xs text-muted">{user.email}</span>
            </span>
            <LanguageSwitch />
            <NotificationLink />
            <Link href="/account" className="rounded-[var(--radius-control)] px-2.5 py-1.5 text-sm font-semibold text-navy-900 hover:bg-navy-50">
              {t("nav.account")}
            </Link>
            <Button variant="ghost" size="sm" onClick={logout}>{t("nav.logout")}</Button>
          </div>
        </div>
      </header>
      {menuOpen && (
        <div className="fixed inset-0 z-40 bg-navy-900/40 md:hidden" onClick={() => setMenuOpen(false)}>
          <aside className="h-full w-72 bg-card py-5" onClick={(event) => event.stopPropagation()}>
            <div className="px-3 pb-4"><Wordmark subtitle={t("app.tagline")} /></div>
            <Sidebar user={user} onNavigate={() => setMenuOpen(false)} />
          </aside>
        </div>
      )}
      <div className="md:flex">
        <aside className="hidden w-60 shrink-0 border-r border-line bg-card py-5 md:block">
          <Sidebar user={user} />
        </aside>
        <main id="main" className="min-w-0 flex-1 px-4 py-6 sm:px-8">
          <div className="mx-auto max-w-6xl">
            <Breadcrumb user={user} />
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

export { LanguageSwitch, Wordmark };
