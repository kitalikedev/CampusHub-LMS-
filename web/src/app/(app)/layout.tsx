"use client";
// Kiểm tra đăng nhập cho mọi trang trong ứng dụng (06 §4.5): không bao giờ quay vòng mãi (ISS-14).
import { useRouter } from "next/navigation";
import { ReactNode, useEffect } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { SkeletonBlock } from "@/components/ui";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function AppLayout({ children }: { children: ReactNode }) {
  const { status, user } = useAuth();
  const router = useRouter();
  const mustChange = user?.must_change_password;

  useEffect(() => {
    if (status === "anonymous") router.replace("/login");
    else if (mustChange) router.replace("/change-password");
  }, [status, mustChange, router]);

  if (status !== "authenticated" || !user || mustChange) {
    return (
      <div className="mx-auto max-w-md px-6 py-24">
        <SkeletonBlock rows={3} />
      </div>
    );
  }
  return <AppShell user={user}>{children}</AppShell>;
}
