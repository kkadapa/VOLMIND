import type { ComponentType, ReactNode } from "react";

export function StatTile({
  label,
  value,
  accent,
  hint,
  icon: Icon,
}: {
  label: string;
  value: ReactNode;
  accent?: string;
  hint?: string;
  icon?: ComponentType<{ size?: number; strokeWidth?: number; color?: string }>;
}) {
  return (
    <div className="glass rounded-2xl px-5 py-4">
      <div className="flex items-center gap-1.5 text-[10.5px] font-semibold uppercase tracking-[0.14em] text-(--ink-muted)">
        {Icon && <Icon size={13} strokeWidth={2.25} />}
        {label}
      </div>
      <div
        className="tabular mt-2 text-[26px] font-bold leading-none tracking-tight"
        style={accent ? { color: accent } : undefined}
      >
        {value}
      </div>
      {hint && <div className="mt-1.5 text-[11.5px] text-(--ink-muted)">{hint}</div>}
    </div>
  );
}
