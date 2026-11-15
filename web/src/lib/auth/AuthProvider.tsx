"use client";
// Phiên đăng nhập (06 §4.5). Token trong localStorage; thông tin người dùng lấy từ GET /me.
import { createContext, ReactNode, useCallback, useContext, useMemo, useSyncExternalStore } from "react";

import { api } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { tokenStore } from "@/lib/auth/tokenStore";
import type { Role, User } from "@/types/api";

type Status = "loading" | "anonymous" | "authenticated";

interface AuthValue {
  status: Status;
  user: User | undefined;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
  refresh: () => void;
}

const AuthContext = createContext<AuthValue | null>(null);
const noopSubscribe = () => () => {};

export function AuthProvider({ children }: { children: ReactNode }) {
  const hydrated = useSyncExternalStore(noopSubscribe, () => true, () => false);
  const token = useSyncExternalStore(tokenStore.subscribe, tokenStore.get, () => null);
  const me = useApi<User>(hydrated && token ? "/me" : null, token ?? "");

  let status: Status = "loading";
  if (hydrated && !token) status = "anonymous";
  else if (me.data) status = "authenticated"; // giữ trạng thái khi đang tải lại /me
  else if (me.error) status = "anonymous";

  const login = useCallback(async (email: string, password: string) => {
    const response = await api.post<{ access_token: string; user: User }>("/auth/login", { email, password });
    tokenStore.set(response.data.access_token);
    return response.data.user;
  }, []);
  const logout = useCallback(() => tokenStore.set(null), []);
  const value = useMemo(
    () => ({ status, user: status === "authenticated" ? me.data : undefined, login, logout, refresh: me.reload }),
    [status, me.data, me.reload, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}

export function homeFor(role: Role): string {
  if (role === "ADMIN") return "/admin/dashboard";
  if (role === "INSTRUCTOR") return "/instructor/dashboard";
  return "/student/dashboard";
}
