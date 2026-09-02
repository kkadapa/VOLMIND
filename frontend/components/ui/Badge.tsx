import { CheckCircle2, CircleDot, SearchX, ShieldAlert } from "lucide-react";
import type { Direction, OpportunityStatus } from "@/lib/api";

const DIRECTION_STYLE: Record<Direction, { label: string; dot: string; text: string }> = {
  bullish: { label: "BULLISH", dot: "var(--status-good)", text: "text-[var(--status-good)]" },
  bearish: { label: "BEARISH", dot: "var(--status-critical)", text: "text-[var(--status-critical)]" },
  neutral: { label: "NEUTRAL", dot: "var(--ink-muted)", text: "text-[var(--ink-muted)]" },
};

export function DirectionBadge({ direction }: { direction: Direction }) {
  const style = DIRECTION_STYLE[direction];
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-white/10 bg-white/[0.05] px-2.5 py-1 text-[11px] font-semibold tracking-wide">
      <span
        className="h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: style.dot }}
        aria-hidden
      />
      <span className={style.text}>{style.label}</span>
    </span>
  );
}

const STATUS_STYLE: Record<
  OpportunityStatus,
  { label: string; color: string; icon: typeof CheckCircle2 }
> = {
  screening: { label: "SCREENING", color: "var(--status-warning)", icon: CircleDot },
  no_trade_diligence: {
    label: "NO TRADE · DILIGENCE",
    color: "var(--status-critical)",
    icon: SearchX,
  },
  no_trade_risk: { label: "NO TRADE · RISK", color: "var(--status-critical)", icon: ShieldAlert },
  cleared: { label: "CLEARED FOR EXECUTION", color: "var(--status-good)", icon: CheckCircle2 },
};

export function StatusBadge({ status }: { status: OpportunityStatus }) {
  const style = STATUS_STYLE[status];
  const Icon = style.icon;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-[11px] font-bold tracking-wide"
      style={{
        color: style.color,
        borderColor: `color-mix(in srgb, ${style.color} 40%, transparent)`,
        backgroundColor: `color-mix(in srgb, ${style.color} 14%, transparent)`,
      }}
    >
      <Icon size={13} strokeWidth={2.25} />
      {style.label}
    </span>
  );
}
