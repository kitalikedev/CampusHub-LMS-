"use client";
import { useCallback } from "react";

import type { ApiError } from "@/lib/api/client";
import { toApiError } from "@/lib/api/client";
import { errorMessage } from "@/lib/i18n/errors";
import { useI18n } from "@/lib/i18n/I18nProvider";

/** Trả về hàm dịch lỗi API (hoặc lỗi bất kỳ) thành câu hiển thị. */
export function useErrorText() {
  const { t, has } = useI18n();
  return useCallback(
    (error: ApiError | unknown) => {
      // AxiosError cũng có `code`/`status`, nên nhận biết ApiError qua trường `params`.
      const apiError = error && typeof error === "object" && "params" in error && "code" in error
        ? (error as ApiError) : toApiError(error);
      return errorMessage(apiError, t, has);
    },
    [t, has],
  );
}
