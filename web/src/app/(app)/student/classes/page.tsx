"use client";
// SCR-S03 Lớp của tôi.
import { ClassList } from "@/features/sections";
import { RoleGate } from "@/lib/auth/RoleGate";

export default function MyClassesPage() {
  return <RoleGate roles={["STUDENT"]}>{() => <ClassList base="/student/classes" />}</RoleGate>;
}
