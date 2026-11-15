"use client";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { SkeletonBlock } from "@/components/ui";
import { homeFor, useAuth } from "@/lib/auth/AuthProvider";

export default function HomePage() {
  const { status, user } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (status === "anonymous") router.replace("/login");
    else if (user) router.replace(user.must_change_password ? "/change-password" : homeFor(user.role));
  }, [status, user, router]);
  return (
    <div className="mx-auto max-w-md px-6 py-24">
      <SkeletonBlock rows={3} />
    </div>
  );
}
