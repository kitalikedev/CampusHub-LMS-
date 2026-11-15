"use client";
// SCR-I02 Lớp phụ trách.
import { ClassList } from "@/features/sections";
import { RoleGate } from "@/lib/auth/RoleGate";

export default function TeachingClassesPage() {
  return <RoleGate roles={["INSTRUCTOR"]}>{() => <ClassList base="/instructor/classes" />}</RoleGate>;
}
