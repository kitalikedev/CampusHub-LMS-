// Menu theo vai trò (04 §2). Thêm tính năng mới vào menu: thêm một dòng ở đây (06 §4.4).
import type { Role } from "@/types/api";

export interface NavItem {
  href: string;
  labelKey: string;
}

export const NAVIGATION: Record<Role, NavItem[]> = {
  STUDENT: [
    { href: "/student/dashboard", labelKey: "nav.dashboard" },
    { href: "/student/registration", labelKey: "nav.registration" },
    { href: "/student/classes", labelKey: "nav.myClasses" },
    { href: "/student/schedule", labelKey: "nav.schedule" },
    { href: "/student/transcript", labelKey: "nav.transcript" },
  ],
  INSTRUCTOR: [
    { href: "/instructor/dashboard", labelKey: "nav.dashboard" },
    { href: "/instructor/classes", labelKey: "nav.teachingClasses" },
    { href: "/instructor/regrades", labelKey: "nav.regrades" },
    { href: "/instructor/schedule", labelKey: "nav.teachingSchedule" },
  ],
  ADMIN: [
    { href: "/admin/dashboard", labelKey: "nav.dashboard" },
    { href: "/admin/users", labelKey: "nav.users" },
    { href: "/admin/semesters", labelKey: "nav.semesters" },
    { href: "/admin/subjects", labelKey: "nav.subjects" },
    { href: "/admin/rooms", labelKey: "nav.rooms" },
    { href: "/admin/sections", labelKey: "nav.sections" },
    { href: "/admin/audit-logs", labelKey: "nav.auditLogs" },
    { href: "/admin/stats", labelKey: "nav.stats" },
  ],
};
