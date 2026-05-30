import { ButtonHTMLAttributes } from "react";

import { cn } from "lib/utils";

const variants = {
  default: "bg-cyan-400 text-slate-950 hover:bg-cyan-300",
  secondary: "bg-slate-900 text-slate-100 hover:bg-slate-800",
};

export function Button({
  className,
  children,
  variant = "default",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: keyof typeof variants }) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-cyan-400/60 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
