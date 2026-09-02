"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { CheckCircle2, Gauge, Radar, ScanSearch, SearchCheck, ShieldCheck, XCircle } from "lucide-react";
import { api, type HealthResponse, type ScanEvent, type ScannedOpportunity } from "@/lib/api";
import { PaperTradingBanner } from "@/components/ui/PaperTradingBanner";
import { StatusBadge } from "@/components/ui/Badge";
import { StatTile } from "@/components/ui/StatTile";
import { TopNav } from "@/components/ui/TopNav";
import { ScanProgress } from "@/components/ScanProgress";

const fmtPct = (v: number | null) => (v == null ? "—" : `${(v * 100).toFixed(1)}%`);

function divergenceColor(score: number | null): string {
  if (score == null) return "var(--ink-muted)";
  return score >= 0 ? "var(--belief-ai)" : "var(--belief-market)";
}

const HOW_IT_WORKS = [
  {
    icon: Radar,
    title: "1. Scout & forecast",
    body: "News, Fundamental, and Probability agents each call an LLM and reason from live Alpaca data to form an independent view.",
  },
  {
    icon: Gauge,
    title: "2. Compare to the market",
    body: "The market's own implied probability is computed directly from the live option chain — no LLM involved.",
  },
  {
    icon: SearchCheck,
    title: "3. Diligence review",
    body: "A second LLM pass independently stress-tests the thesis. A thesis that doesn't clear review stops here — no strategy is ever built.",
  },
  {
    icon: ShieldCheck,
    title: "4. Risk & paper execution",
    body: "Only a thesis that clears diligence gets a strategy, a risk check, and — if cleared — a paper order. Never live.",
  },
];

interface ScanRun {
  ticker: string;
  completedNodes: Set<string>;
  finished: boolean;
  errored: boolean;
  errorMessage?: string;
}

export default function MarketRadarPage() {
  const router = useRouter();
  const [opportunities, setOpportunities] = useState<ScannedOpportunity[]>([]);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [symbolsInput, setSymbolsInput] = useState("AAPL");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeRuns, setActiveRuns] = useState<ScanRun[]>([]);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    let cancelled = false;

    api
      .opportunities()
      .then((data) => !cancelled && setOpportunities(data))
      .catch(() => {
        // No scans yet -- empty state handles this.
      });
    api
      .health()
      .then((data) => !cancelled && setHealth(data))
      .catch(() => !cancelled && setHealth(null));

    return () => {
      cancelled = true;
      eventSourceRef.current?.close();
    };
  }, []);

  function runScan() {
    const symbols = symbolsInput
      .split(",")
      .map((s) => s.trim().toUpperCase())
      .filter(Boolean);
    if (symbols.length === 0 || scanning) return;

    setScanning(true);
    setError(null);
    setActiveRuns(symbols.map((ticker) => ({ ticker, completedNodes: new Set(), finished: false, errored: false })));

    const source = api.streamScan(symbols, (event: ScanEvent) => {
      handleScanEvent(event);
    });
    eventSourceRef.current = source;

    source.onerror = () => {
      source.close();
      setScanning(false);
    };

    function handleScanEvent(event: ScanEvent) {
      switch (event.type) {
        case "symbol_start":
          break;
        case "agent_done":
          setActiveRuns((prev) =>
            prev.map((run) =>
              run.ticker === event.ticker
                ? { ...run, completedNodes: new Set(run.completedNodes).add(event.node) }
                : run,
            ),
          );
          break;
        case "symbol_error":
          setActiveRuns((prev) =>
            prev.map((run) =>
              run.ticker === event.ticker
                ? { ...run, finished: true, errored: true, errorMessage: event.message }
                : run,
            ),
          );
          break;
        case "opportunity_complete":
          setActiveRuns((prev) =>
            prev.map((run) => (run.ticker === event.ticker ? { ...run, finished: true } : run)),
          );
          setOpportunities((prev) => {
            const byTicker = new Map(prev.map((o) => [o.ticker, o]));
            byTicker.set(event.ticker, event.data);
            return Array.from(byTicker.values()).sort(
              (a, b) => b.opportunity_score - a.opportunity_score,
            );
          });
          break;
        case "scan_complete":
          source.close();
          setScanning(false);
          break;
      }
    }
  }

  return (
    <div className="flex min-h-full flex-col">
      <PaperTradingBanner />

      <header className="border-b border-white/[0.09] px-6 py-6 sm:px-10">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div
                className="flex h-10 w-10 items-center justify-center rounded-xl text-base font-black text-white shadow-sm"
                style={{
                  background: "linear-gradient(135deg, var(--belief-ai), var(--agent-diligence))",
                }}
              >
                V
              </div>
              <h1 className="text-2xl font-bold tracking-tight">VOLMIND</h1>
            </div>
            <p className="mt-1.5 text-[13px] text-(--ink-muted)">
              Trade the divergence between AI belief and market belief.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-white/[0.09] bg-white/[0.04] px-3 py-1.5 sm:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-(--status-good)" />
              <span className="text-[11.5px] text-(--ink-muted)">
                LLM: <span className="font-semibold text-(--ink-secondary)">{health?.llm_provider ?? "…"}</span>
              </span>
            </div>
            <TopNav />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-9 sm:px-10">
        {/* How it works */}
        <section className="mb-8 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {HOW_IT_WORKS.map((step) => (
            <div key={step.title} className="glass rounded-2xl p-4">
              <step.icon size={18} strokeWidth={2} color="var(--belief-ai)" />
              <div className="mt-2.5 text-[13px] font-bold tracking-tight">{step.title}</div>
              <p className="mt-1 text-[12px] leading-relaxed text-(--ink-muted)">{step.body}</p>
            </div>
          ))}
        </section>

        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight">Market Divergence Radar</h2>
            <p className="text-[13px] text-(--ink-muted)">
              Independent AI probability vs. market-implied probability, per underlying.
            </p>
          </div>
          <div className="glass flex items-center gap-2 rounded-2xl p-2">
            <input
              value={symbolsInput}
              onChange={(e) => setSymbolsInput(e.target.value)}
              placeholder="AAPL, MSFT, NVDA"
              className="tabular w-48 bg-transparent px-3 py-2 text-[14px] font-medium tracking-wide outline-none placeholder:text-(--ink-faint)"
              onKeyDown={(e) => e.key === "Enter" && runScan()}
            />
            <button
              onClick={runScan}
              disabled={scanning}
              className="flex items-center gap-1.5 rounded-xl px-4 py-2 text-[13px] font-bold tracking-wide text-white shadow-sm shadow-blue-900/20 transition-opacity disabled:opacity-60"
              style={{
                background: "linear-gradient(135deg, var(--belief-ai), var(--agent-diligence))",
              }}
            >
              <ScanSearch size={15} strokeWidth={2.25} />
              {scanning ? "SCANNING…" : "RUN SCAN"}
            </button>
          </div>
        </div>

        {error && (
          <div
            className="mb-4 flex items-center gap-2 rounded-xl border px-4 py-3 text-[13px]"
            style={{
              borderColor: "color-mix(in srgb, var(--status-critical) 40%, transparent)",
              backgroundColor: "color-mix(in srgb, var(--status-critical) 10%, transparent)",
              color: "var(--status-critical)",
            }}
          >
            <XCircle size={15} strokeWidth={2.25} />
            {error}
          </div>
        )}

        {activeRuns.length > 0 && (
          <div className="mb-5 space-y-3">
            {activeRuns.map((run) => (
              <div key={run.ticker}>
                <ScanProgress
                  ticker={run.ticker}
                  completedNodes={run.completedNodes}
                  finished={run.finished}
                  errored={run.errored}
                />
                {run.errored && run.errorMessage && (
                  <p className="mt-1.5 pl-1 text-[11.5px] text-(--status-critical)">{run.errorMessage}</p>
                )}
              </div>
            ))}
          </div>
        )}

        {opportunities.length === 0 && activeRuns.length === 0 ? (
          <div className="glass flex flex-col items-center gap-3 rounded-2xl px-6 py-20 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/[0.05]">
              <Radar size={22} strokeWidth={1.75} color="var(--ink-muted)" />
            </div>
            <p className="text-[15px] font-semibold text-(--ink-secondary)">No opportunities scanned yet</p>
            <p className="max-w-sm text-[13px] leading-relaxed text-(--ink-muted)">
              Enter one or more tickers above and run a scan to see the AI agents form an
              independent view against the market-implied probability.
            </p>
          </div>
        ) : opportunities.length > 0 ? (
          <div className="glass overflow-hidden rounded-2xl">
            <div className="overflow-x-auto">
              <table className="w-full min-w-[900px] border-collapse text-left text-[13px]">
                <thead>
                  <tr className="border-b border-white/[0.09] text-[10.5px] uppercase tracking-[0.1em] text-(--ink-muted)">
                    <th className="px-4 py-3.5 font-semibold">Ticker</th>
                    <th className="px-4 py-3.5 font-semibold">Price</th>
                    <th className="px-4 py-3.5 font-semibold">Catalyst</th>
                    <th className="px-4 py-3.5 font-semibold">AI Prob.</th>
                    <th className="px-4 py-3.5 font-semibold">Market Prob.</th>
                    <th className="px-4 py-3.5 font-semibold">Divergence</th>
                    <th className="px-4 py-3.5 font-semibold">Confidence</th>
                    <th className="px-4 py-3.5 font-semibold">Opp. Score</th>
                    <th className="px-4 py-3.5 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {opportunities.map((o) => {
                    const aiProb = o.probability_forecast
                      ? 1 -
                        (o.probability_forecast.probabilities["-10%"] ?? 0) -
                        (o.probability_forecast.probabilities["-5%"] ?? 0) -
                        (o.probability_forecast.probabilities["flat"] ?? 0) / 2
                      : null;
                    const bigGap = Math.abs(o.divergence_score ?? 0) >= 0.2;
                    return (
                      <tr
                        key={o.ticker}
                        onClick={() => router.push(`/opportunity/${o.ticker}`)}
                        className="cursor-pointer border-b border-white/[0.06] transition-colors last:border-0 hover:bg-white/[0.04]"
                      >
                        <td className="px-4 py-3.5">
                          <Link
                            href={`/opportunity/${o.ticker}`}
                            onClick={(e) => e.stopPropagation()}
                            className="font-bold tracking-tight hover:underline"
                          >
                            {o.ticker}
                          </Link>
                        </td>
                        <td className="tabular px-4 py-3.5 text-(--ink-secondary)">${o.price.toFixed(2)}</td>
                        <td
                          className="max-w-[220px] truncate px-4 py-3.5 text-(--ink-muted)"
                          title={o.news_assessment?.what_changed ?? undefined}
                        >
                          {o.news_assessment?.what_changed ?? "—"}
                        </td>
                        <td className="tabular px-4 py-3.5 font-semibold" style={{ color: "var(--belief-ai)" }}>
                          {fmtPct(aiProb)}
                        </td>
                        <td className="tabular px-4 py-3.5 font-semibold" style={{ color: "var(--belief-market)" }}>
                          {fmtPct(o.market_implied_probability)}
                        </td>
                        <td
                          className="tabular px-4 py-3.5 font-bold"
                          style={{ color: divergenceColor(o.divergence_score) }}
                        >
                          <span
                            className={bigGap ? "rounded px-1.5 py-0.5" : ""}
                            style={
                              bigGap
                                ? {
                                    backgroundColor: `color-mix(in srgb, ${divergenceColor(o.divergence_score)} 16%, transparent)`,
                                  }
                                : undefined
                            }
                          >
                            {o.divergence_score != null && o.divergence_score >= 0 ? "+" : ""}
                            {fmtPct(o.divergence_score)}
                          </span>
                        </td>
                        <td className="tabular px-4 py-3.5 text-(--ink-secondary)">
                          {fmtPct(o.probability_forecast?.confidence ?? null)}
                        </td>
                        <td className="tabular px-4 py-3.5 text-(--ink-secondary)">
                          {o.opportunity_score.toFixed(3)}
                        </td>
                        <td className="px-4 py-3.5">
                          <StatusBadge status={o.status} />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}

        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatTile icon={Radar} label="Scanned" value={opportunities.length} />
          <StatTile
            icon={XCircle}
            label="No Trade"
            value={opportunities.filter((o) => o.status.startsWith("no_trade")).length}
            accent="var(--status-critical)"
          />
          <StatTile
            icon={CheckCircle2}
            label="Cleared"
            value={opportunities.filter((o) => o.status === "cleared").length}
            accent="var(--status-good)"
          />
          <StatTile
            icon={ShieldCheck}
            label="Mode"
            value={health?.paper_trading ? "PAPER" : "BLOCKED"}
            accent={health?.paper_trading ? "var(--status-good)" : "var(--status-critical)"}
            hint={health?.paper_trading ? "Execution guard: open" : "Execution guard: closed"}
          />
        </div>
      </main>
    </div>
  );
}
