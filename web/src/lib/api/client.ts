// Gọi API: gắn token, chuẩn hóa lỗi thành { code, params } (06 §2.5, ADR-08).
import axios, { AxiosError } from "axios";

import { tokenStore } from "@/lib/auth/tokenStore";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5001/api";

export const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((config) => {
  const token = tokenStore.get();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: ApiErrorBody }>) => {
    const code = error.response?.data?.error?.code;
    // Token hết hạn / không hợp lệ: xóa token, AuthProvider sẽ chuyển về trang đăng nhập.
    if (error.response?.status === 401 && code === "AUTH_REQUIRED") tokenStore.set(null);
    if (code === "ACCOUNT_DISABLED") tokenStore.set(null);
    return Promise.reject(error);
  },
);

interface ApiErrorBody {
  code: string;
  message: string;
  params: Record<string, unknown>;
}

export interface ApiError {
  code: string;
  params: Record<string, unknown>;
  status: number;
}

export function toApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const body = (error.response?.data as { error?: ApiErrorBody } | undefined)?.error;
    if (body?.code) return { code: body.code, params: body.params || {}, status: error.response?.status ?? 0 };
    if (!error.response) return { code: "NETWORK_ERROR", params: {}, status: 0 };
    return { code: "INTERNAL_ERROR", params: {}, status: error.response.status };
  }
  return { code: "INTERNAL_ERROR", params: {}, status: 0 };
}

/** Tải file cần token (không mở link trực tiếp được). */
export async function downloadFile(fileId: number, filename: string): Promise<void> {
  const response = await api.get<Blob>(`/files/${fileId}`, { responseType: "blob" });
  saveBlob(response.data, filename);
}

export function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
