const fmtPct = (v: number) => `${(v * 100).toFixed(1)}%`;

function BeliefBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const pct = Math.max(0, Math.min(1, value)) * 100;
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between text-[11px]">
        <span className="flex items-center gap-1.5 font-semibold text-[color:var(--ink-secondary)]">
          <span
            className="h-2 w-2 rounded-[2px]"
            style={{ backgroundColor: color }}
            aria-hidden
          />
          {label}
        </span>
        <span className="tabular font-semibold" style={{ color }}>
          {fmtPct(value)}
        </span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-white/[0.08]">
        <div
          className="h-full rounded-full transition-[width] duration-500 ease-out"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

/** Diverging comparison of P(upside): AI belief vs. market-implied belief. */
export function BeliefComparisonChart({
  aiProbability,
  marketProbability,
}: {
  aiProbability: number;
  marketProbability: number;
}) {
  const gap = aiProbability - marketProbability;
  const gapColor = gap >= 0 ? "var(--belief-ai)" : "var(--belief-market)";
  return (
    <div className="space-y-3.5">
      <BeliefBar label="AI BELIEF · P(upside)" value={aiProbability} color="var(--belief-ai)" />
      <BeliefBar
        label="MARKET-IMPLIED · P(upside)"
        value={marketProbability}
        color="var(--belief-market)"
      />
      <div className="flex items-center justify-between border-t border-white/[0.09] pt-2.5 text-[11px]">
        <span className="text-[color:var(--ink-muted)]">DIVERGENCE</span>
        <span className="tabular font-bold" style={{ color: gapColor }}>
          {gap >= 0 ? "+" : ""}
          {fmtPct(gap)}
        </span>
      </div>
    </div>
  );
}
