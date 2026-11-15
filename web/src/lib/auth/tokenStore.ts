// Token đăng nhập trong localStorage (ADR-13), đọc qua useSyncExternalStore.
const KEY = "campushub.token";
const EVENT = "campushub:token";

function read(): string | null {
  try {
    return window.localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export const tokenStore = {
  get(): string | null {
    return typeof window === "undefined" ? null : read();
  },
  set(token: string | null): void {
    try {
      if (token) window.localStorage.setItem(KEY, token);
      else window.localStorage.removeItem(KEY);
    } catch {
      /* trình duyệt chặn storage: bỏ qua */
    }
    window.dispatchEvent(new Event(EVENT));
  },
  subscribe(listener: () => void): () => void {
    window.addEventListener(EVENT, listener);
    window.addEventListener("storage", listener);
    return () => {
      window.removeEventListener(EVENT, listener);
      window.removeEventListener("storage", listener);
    };
  },
};
