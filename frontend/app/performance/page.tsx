"use client";

import { useEffect, useState } from "react";
import {
  Activity,
  CheckCircle2,
  DollarSign,
  RefreshCw,
  Target,
  TrendingUp,
} from "lucide-react";
import {
  api,
  type AgentReputationEntry,
  type PerformanceSummary,
  type PositionSnapshot,
  type Trade,
} from "@/lib/api";
import { PaperTradingBanner } from "@/components/ui/PaperTradingBanner";
import { StatTile } from "@/components/ui/StatTile";
import { TopNav } from "@/components/ui/TopNav";
import { EquityCurveChart } from "@/components/charts/EquityCurveChart";

const fmtUsd = (v: number | null) => (v == null ? "—" : `${v < 0 ? "-" : ""}$${Math.abs(v).toFixed(2)}`);
const fmtPct = (v: number | null) => (v == null ? "—" : `${(v * 100).toFixed(0)}%`);
const pnlColor = (v: number | null) => (v == null ? "var(--ink-muted)" : v >= 0 ? "var(--status-good)" : "var(--status-critical)");

const AGENT_LABELS: Record<string, string> = {
  news_agent: "News",
  fundamental_agent: "Fundamental",
  probability_agent: "Probability",
  diligence_agent: "Diligence",
  risk_agent: "Risk",
};

export default function PerformancePage() {
  const [performance, setPerformance] = useState<PerformanceSummary | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [livePositions, setLivePositions] = useState<PositionSnapshot[]>([]);
  const [reputation, setReputation] = useState<AgentReputationEntry[]>([]);
  const [monitoring, setMonitoring] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function load() {
    api.performance().then(setPerformance).catch(() => setPerformance(null));
    api.trades().then(setTrades).catch(() => setTrades([]));
    api.positions().then(setLivePositions).catch(() => setLivePositions([]));
    api.reputation().then(setReputation).catch(() => setReputation([]));
  }

  useEffect(load, []);

  async function runMonitor() {
    setMonitoring(true);
    setError(null);
    try {
      await api.monitorPositions();
      load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to run position monitor.");
    } finally {
      setMonitoring(false);
    }
  }

  const openTrades = trades.filter((t) => t.status === "open");
  const closedTrades = [...trades.filter((t) => t.status === "closed")].sort((a, b) =>
    (b.closed_at ?? "").localeCompare(a.closed_at ?? ""),
  );
  const liveBySymbol = new Map(livePositions.map((p) => [p.symbol, p]));

  return (
    <div className="flex min-h-full flex-col">
      <PaperTradingBanner />

      <header className="border-b border-white/[0.09] px-6 py-6 sm:px-10">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Performance</h1>
            <p className="mt-1.5 text-[13px] text-(--ink-muted)">
              Realized P&L, open positions, and agent track record over the competition.
            </p>
          </div>
          <TopNav />
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-9 sm:px-10">
        {error && (
          <div
            className="mb-4 rounded-xl border px-4 py-3 text-[13px]"
            style={{
              borderColor: "color-mix(in srgb, var(--status-critical) 40%, transparent)",
              backgroundColor: "color-mix(in srgb, var(--status-critical) 10%, transparent)",
              color: "var(--status-critical)",
            }}
          >
            {error}
          </div>
        )}

        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatTile
            icon={DollarSign}
            label="Realized P&L"
            value={fmtUsd(performance?.total_realized_pnl ?? null)}
            accent={pnlColor(performance?.total_realized_pnl ?? null)}
          />
          <StatTile icon={Target} label="Win Rate" value={fmtPct(performance?.win_rate ?? null)} />
          <StatTile icon={Activity} label="Open Positions" value={performance?.open_count ?? "—"} />
          <StatTile icon={CheckCircle2} label="Closed Trades" value={performance?.closed_count ?? "—"} />
        </div>

        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-bold tracking-tight">Equity curve</h2>
          <button
            onClick={runMonitor}
            disabled={monitoring}
            className="flex items-center gap-1.5 rounded-xl border border-white/[0.09] bg-white/[0.04] px-3.5 py-2 text-[12px] font-bold tracking-wide text-(--ink-secondary) transition-opacity disabled:opacity-60"
          >
            <RefreshCw size={13} strokeWidth={2.25} className={monitoring ? "animate-spin" : ""} />
            {monitoring ? "MONITORING…" : "RUN POSITION MONITOR"}
          </button>
        </div>
        <div className="glass mb-8 rounded-2xl p-5">
          <EquityCurveChart equityCurve={performance?.equity_curve ?? []} />
        </div>

        <h2 className="mb-4 text-xl font-bold tracking-tight">Open positions</h2>
        <div className="glass mb-8 overflow-hidden rounded-2xl">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-[13px]">
              <thead>
                <tr className="border-b border-white/[0.09] text-[10.5px] uppercase tracking-[0.1em] text-(--ink-muted)">
                  <th className="px-4 py-3.5 font-semibold">Symbol</th>
                  <th className="px-4 py-3.5 font-semibold">Strategy</th>
                  <th className="px-4 py-3.5 font-semibold">Qty</th>
                  <th className="px-4 py-3.5 font-semibold">Entry cost</th>
                  <th className="px-4 py-3.5 font-semibold">Opened</th>
                  <th className="px-4 py-3.5 font-semibold">Live unrealized P&L</th>
                </tr>
              </thead>
              <tbody>
                {openTrades.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-10 text-center text-(--ink-muted)">
                      No open positions. Run a scan to look for the next opportunity.
                    </td>
                  </tr>
                ) : (
                  openTrades.map((trade) => {
                    const live = liveBySymbol.get(trade.legs[0]?.symbol ?? "");
                    return (
                      <tr key={trade.id} className="border-b border-white/[0.06] last:border-0">
                        <td className="px-4 py-3.5 font-bold tracking-tight">{trade.underlying_symbol}</td>
                        <td className="px-4 py-3.5 text-(--ink-secondary)">{trade.strategy_name}</td>
                        <td className="tabular px-4 py-3.5 text-(--ink-secondary)">{trade.quantity}</td>
                        <td className="tabular px-4 py-3.5 text-(--ink-secondary)">${trade.entry_cost.toFixed(2)}</td>
                        <td className="px-4 py-3.5 text-(--ink-muted)">
                          {trade.opened_at ? new Date(trade.opened_at).toLocaleDateString() : "—"}
                        </td>
                        <td className="tabular px-4 py-3.5 font-semibold" style={{ color: pnlColor(live?.unrealized_pl ?? null) }}>
                          {live ? fmtUsd(live.unrealized_pl) : "—"}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        <h2 className="mb-4 text-xl font-bold tracking-tight">Closed trades</h2>
        <div className="glass mb-8 overflow-hidden rounded-2xl">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] border-collapse text-left text-[13px]">
              <thead>
                <tr className="border-b border-white/[0.09] text-[10.5px] uppercase tracking-[0.1em] text-(--ink-muted)">
                  <th className="px-4 py-3.5 font-semibold">Symbol</th>
                  <th className="px-4 py-3.5 font-semibold">Strategy</th>
                  <th className="px-4 py-3.5 font-semibold">Closed</th>
                  <th className="px-4 py-3.5 font-semibold">Realized P&L</th>
                  <th className="px-4 py-3.5 font-semibold">Result</th>
                </tr>
              </thead>
              <tbody>
                {closedTrades.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-10 text-center text-(--ink-muted)">
                      No trades closed yet.
                    </td>
                  </tr>
                ) : (
                  closedTrades.map((trade) => (
                    <tr key={trade.id} className="border-b border-white/[0.06] last:border-0">
                      <td className="px-4 py-3.5 font-bold tracking-tight">{trade.underlying_symbol}</td>
                      <td className="px-4 py-3.5 text-(--ink-secondary)">{trade.strategy_name}</td>
                      <td className="px-4 py-3.5 text-(--ink-muted)">
                        {trade.closed_at ? new Date(trade.closed_at).toLocaleString() : "—"}
                      </td>
                      <td className="tabular px-4 py-3.5 font-bold" style={{ color: pnlColor(trade.realized_pnl) }}>
                        {fmtUsd(trade.realized_pnl)}
                      </td>
                      <td className="px-4 py-3.5">
                        <span
                          className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-bold tracking-wide"
                          style={{
                            color: pnlColor(trade.realized_pnl),
                            borderColor: `color-mix(in srgb, ${pnlColor(trade.realized_pnl)} 40%, transparent)`,
                            backgroundColor: `color-mix(in srgb, ${pnlColor(trade.realized_pnl)} 14%, transparent)`,
                          }}
                        >
                          {(trade.realized_pnl ?? 0) >= 0 ? "WIN" : "LOSS"}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <h2 className="mb-4 text-xl font-bold tracking-tight">Agent reputation</h2>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {reputation.map((entry) => (
            <div key={entry.agent_name} className="glass rounded-2xl p-4">
              <div className="flex items-center gap-1.5 text-[10.5px] font-semibold uppercase tracking-[0.12em] text-(--ink-muted)">
                <TrendingUp size={13} strokeWidth={2.25} />
                {AGENT_LABELS[entry.agent_name] ?? entry.agent_name}
              </div>
              <div className="tabular mt-2 text-[22px] font-bold leading-none tracking-tight">
                {entry.trade_count > 0 ? `${entry.correct_count}/${entry.trade_count}` : "—"}
              </div>
              <div className="mt-1.5 text-[11.5px] text-(--ink-muted)">
                {entry.trade_count > 0
                  ? `${Math.round(entry.reputation_weight * 100)}% correct on closed trades`
                  : "No closed trades yet"}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
