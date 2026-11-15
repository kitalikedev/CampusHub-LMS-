"use client";
import { ReactNode } from "react";

import { Forbidden } from "@/components/ui";
import { useAuth } from "@/lib/auth/AuthProvider";
import type { Role, User } from "@/types/api";

/** Chặn trang theo vai trò ở giao diện. Backend vẫn kiểm tra quyền (BR-GEN-02). */
export function RoleGate({ roles, children }: { roles: Role[]; children: (user: User) => ReactNode }) {
  const { user } = useAuth();
  if (!user) return null;
  if (!roles.includes(user.role)) return <Forbidden />;
  return <>{children(user)}</>;
}
