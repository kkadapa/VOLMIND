import type { ComponentType, ReactNode } from "react";
import type { Direction } from "@/lib/api";
import { DirectionBadge } from "@/components/ui/Badge";

export function AgentCard({
  name,
  role,
  accent,
  icon: Icon,
  direction,
  confidence,
  headline,
  bullets,
  footer,
}: {
  name: string;
  role: string;
  accent: string;
  icon: ComponentType<{ size?: number; strokeWidth?: number; color?: string }>;
  direction?: Direction;
  confidence: number;
  headline: string;
  bullets: string[];
  footer?: ReactNode;
}) {
  return (
    <div
      className="glass glass-hover relative overflow-hidden rounded-2xl p-5"
      style={{ borderLeft: `3px solid ${accent}` }}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2.5">
          <div
            className="mt-0.5 flex h-8 w-8 flex-none items-center justify-center rounded-lg"
            style={{ backgroundColor: `color-mix(in srgb, ${accent} 14%, transparent)` }}
          >
            <Icon size={16} strokeWidth={2} color={accent} />
          </div>
          <div>
            <div className="text-[14px] font-bold tracking-tight text-(--ink-primary)">{name}</div>
            <div className="text-[10.5px] uppercase tracking-[0.12em] text-(--ink-muted)">{role}</div>
          </div>
        </div>
        {direction && <DirectionBadge direction={direction} />}
      </div>

      <p className="mt-3.5 text-[13px] leading-relaxed text-(--ink-secondary)">{headline}</p>

      {bullets.length > 0 && (
        <ul className="mt-3 space-y-1.5">
          {bullets.slice(0, 3).map((b, i) => (
            <li key={i} className="flex gap-1.5 text-[12px] leading-snug text-(--ink-muted)">
              <span className="mt-1.5 h-1 w-1 flex-none rounded-full bg-current opacity-60" />
              {b}
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4 flex items-center justify-between border-t border-white/[0.08] pt-3">
        <span className="text-[10.5px] uppercase tracking-wide text-(--ink-muted)">Confidence</span>
        <div className="flex items-center gap-2">
          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-white/[0.08]">
            <div
              className="h-full rounded-full"
              style={{ width: `${confidence * 100}%`, backgroundColor: accent }}
            />
          </div>
          <span className="tabular text-[11.5px] font-semibold" style={{ color: accent }}>
            {Math.round(confidence * 100)}%
          </span>
        </div>
      </div>
      {footer}
    </div>
  );
}
