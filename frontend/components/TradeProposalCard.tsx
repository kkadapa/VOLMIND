import { Layers } from "lucide-react";
import type { ProposedTrade } from "@/lib/api";

export function TradeProposalCard({
  trade,
  riskApproved,
  riskNotes,
}: {
  trade: ProposedTrade;
  riskApproved: boolean | null;
  riskNotes: string | null;
}) {
  const color = riskApproved ? "var(--status-good)" : "var(--status-critical)";
  return (
    <div className="glass rounded-2xl p-5" style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2.5">
          <div
            className="mt-0.5 flex h-8 w-8 flex-none items-center justify-center rounded-lg"
            style={{ backgroundColor: `color-mix(in srgb, ${color} 14%, transparent)` }}
          >
            <Layers size={16} strokeWidth={2} color={color} />
          </div>
          <div>
            <div className="text-[14px] font-bold tracking-tight">Options Architect</div>
            <div className="text-[10.5px] uppercase tracking-[0.12em] text-(--ink-muted)">
              {trade.strategy_name.replaceAll("_", " ")}
            </div>
          </div>
        </div>
        <span
          className="rounded-full border px-2.5 py-1 text-[11px] font-bold"
          style={{
            color,
            borderColor: `color-mix(in srgb, ${color} 40%, transparent)`,
            backgroundColor: `color-mix(in srgb, ${color} 14%, transparent)`,
          }}
        >
          {riskApproved ? "RISK: CLEARED" : "RISK: FLAGGED"}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2.5">
        <Metric label="Entry cost" value={`$${trade.entry_cost.toFixed(2)}`} />
        <Metric label="Max loss" value={`$${trade.max_loss.toFixed(2)}`} accent="var(--status-critical)" />
        <Metric
          label="Max profit"
          value={trade.max_profit != null ? `$${trade.max_profit.toFixed(2)}` : "Unlimited"}
          accent="var(--status-good)"
        />
      </div>

      <div className="mt-4 space-y-1.5">
        {trade.legs.map((leg) => (
          <div
            key={leg.symbol}
            className="tabular flex items-center justify-between rounded-lg bg-white/[0.05] px-3 py-2.5 text-[12px]"
          >
            <span className="font-semibold uppercase text-(--ink-secondary)">
              {leg.option_type} ${leg.strike}
            </span>
            <span className="text-(--ink-muted)">
              bid {leg.bid.toFixed(2)} / ask {leg.ask.toFixed(2)}
            </span>
            <span className="text-(--ink-muted)">{leg.expiry.slice(0, 10)}</span>
          </div>
        ))}
      </div>

      {riskNotes && <p className="mt-3.5 text-[12px] leading-relaxed text-(--ink-muted)">{riskNotes}</p>}
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="rounded-lg bg-white/[0.05] px-2.5 py-2.5">
      <div className="text-[9.5px] uppercase tracking-wide text-(--ink-muted)">{label}</div>
      <div className="tabular mt-0.5 text-[13.5px] font-bold" style={accent ? { color: accent } : undefined}>
        {value}
      </div>
    </div>
  );
}
