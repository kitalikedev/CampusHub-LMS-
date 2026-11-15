"use client";
// SCR-S06 Thời khóa biểu (FR-TRN-02).
import { SchedulePage } from "@/features/schedule";
import { RoleGate } from "@/lib/auth/RoleGate";

export default function StudentSchedulePage() {
  return <RoleGate roles={["STUDENT"]}>{() => <SchedulePage titleKey="nav.schedule" linkBase="/student/classes" />}</RoleGate>;
}
