import Link from "next/link";
import { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "danger" | "ghost";
type Size = "sm" | "md";

const base =
  "inline-flex items-center justify-center gap-2 rounded-[var(--radius-control)] font-medium transition-colors duration-150 " +
  "disabled:cursor-not-allowed disabled:opacity-50 whitespace-nowrap";
const variants: Record<Variant, string> = {
  primary: "bg-navy-900 text-white hover:bg-navy-800",
  secondary: "border border-navy-900 bg-card text-navy-900 hover:bg-navy-50",
  danger: "bg-crimson-600 text-white hover:bg-crimson-700",
  ghost: "text-navy-700 underline-offset-4 hover:bg-navy-50 hover:underline",
};
const sizes: Record<Size, string> = { sm: "h-8 px-3 text-sm font-semibold", md: "h-10 px-4 text-[0.95rem] font-semibold" };

export function buttonClass(variant: Variant = "primary", size: Size = "md", extra = ""): string {
  return `${base} ${variants[variant]} ${sizes[size]} ${extra}`;
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
}

export function Button({ variant = "primary", size = "md", loading, disabled, className = "", children, type = "button",
                         ...rest }: ButtonProps) {
  return (
    <button type={type} className={buttonClass(variant, size, className)} disabled={disabled || loading}
            aria-busy={loading || undefined} {...rest}>
      {loading && <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden />}
      {children}
    </button>
  );
}

export function ButtonLink({ href, variant = "secondary", size = "md", children, className = "" }: {
  href: string; variant?: Variant; size?: Size; children: ReactNode; className?: string;
}) {
  return <Link href={href} className={buttonClass(variant, size, className)}>{children}</Link>;
}
