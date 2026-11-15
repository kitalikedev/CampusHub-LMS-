"use client";
// SCR-I06 Lịch dạy (FR-TRN-02).
import { SchedulePage } from "@/features/schedule";
import { RoleGate } from "@/lib/auth/RoleGate";

export default function TeachingSchedulePage() {
  return <RoleGate roles={["INSTRUCTOR"]}>{() => <SchedulePage titleKey="nav.teachingSchedule" linkBase="/instructor/classes" />}</RoleGate>;
}
