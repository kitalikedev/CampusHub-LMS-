"use client";
// Hook tải dữ liệu chung: { data, error, loading, reload }. Không gọi setState đồng bộ trong effect.
import { useCallback, useEffect, useState } from "react";

import { api, ApiError, toApiError } from "@/lib/api/client";

interface State<T> {
  base: string | null; // url + extraKey mà data thuộc về
  key: string | null; // base + lần tải
  data?: T;
  error?: ApiError;
}

export interface ApiResult<T> {
  data: T | undefined;
  error: ApiError | undefined;
  loading: boolean;
  reload: () => void;
}

/** url = null: chưa tải. extraKey: buộc tải lại khi giá trị đổi (ví dụ token). */
export function useApi<T>(url: string | null, extraKey = ""): ApiResult<T> {
  const [nonce, setNonce] = useState(0);
  const [state, setState] = useState<State<T>>({ base: null, key: null });
  const base = url ? `${url}|${extraKey}` : null;
  const key = base ? `${base}|${nonce}` : null;

  useEffect(() => {
    if (!url || !key) return;
    let active = true;
    api
      .get<T>(url)
      .then((response) => {
        if (active) setState({ base, key, data: response.data });
      })
      .catch((error: unknown) => {
        if (active) setState((prev) => ({ base, key, data: prev.base === base ? prev.data : undefined,
                                          error: toApiError(error) }));
      });
    return () => {
      active = false;
    };
  }, [url, base, key]);

  const reload = useCallback(() => setNonce((n) => n + 1), []);
  const sameBase = base !== null && state.base === base;
  return {
    data: sameBase ? state.data : undefined,
    error: state.key === key ? state.error : undefined,
    loading: Boolean(url) && state.key !== key,
    reload,
  };
}
