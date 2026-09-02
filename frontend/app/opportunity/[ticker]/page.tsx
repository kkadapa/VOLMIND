"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import {
  ArrowLeft,
  Building2,
  ClipboardList,
  Gauge,
  Loader2,
  Newspaper,
  Sparkles,
  TriangleAlert,
} from "lucide-react";
import { api, type ScannedOpportunity } from "@/lib/api";
import { PaperTradingBanner } from "@/components/ui/PaperTradingBanner";
import { StatusBadge } from "@/components/ui/Badge";
import { StatTile } from "@/components/ui/StatTile";
import { AgentCard } from "@/components/AgentCard";
import { DiligenceReportCard } from "@/components/DiligenceReportCard";
import { TradeProposalCard } from "@/components/TradeProposalCard";
import { BeliefComparisonChart } from "@/components/charts/BeliefComparisonChart";
import { ProbabilityDistributionChart } from "@/components/charts/ProbabilityDistributionChart";

export default function OpportunityDetailPage({
  params,
}: {
  params: Promise<{ ticker: string }>;
}) {
  const { ticker } = use(params);
  const [data, setData] = useState<ScannedOpportunity | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    api
      .opportunity(ticker)
      .then(setData)
      .catch(() => setNotFound(true));
  }, [ticker]);

  if (notFound) {
    return (
      <div className="flex min-h-full flex-col">
        <PaperTradingBanner />
        <main className="mx-auto flex max-w-2xl flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
          <TriangleAlert size={22} strokeWidth={1.75} color="var(--ink-muted)" />
          <p className="text-[15px] font-semibold">No scan on record for {ticker.toUpperCase()}</p>
          <Link
            href="/"
            className="flex items-center gap-1 text-[13px] text-(--belief-ai) underline underline-offset-2"
          >
            <ArrowLeft size={13} strokeWidth={2.25} /> Back to Market Radar
          </Link>
        </main>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex min-h-full flex-col">
        <PaperTradingBanner />
        <main className="mx-auto flex max-w-2xl flex-1 items-center justify-center gap-2 text-[13px] text-(--ink-muted)">
          <Loader2 size={15} strokeWidth={2.25} className="animate-spin" />
          Loading {ticker.toUpperCase()}…
        </main>
      </div>
    );
  }

  const aiUpside = data.probability_forecast
    ? (data.probability_forecast.probabilities["+10%"] ?? 0) +
      (data.probability_forecast.probabilities["+5%"] ?? 0) +
      (data.probability_forecast.probabilities["flat"] ?? 0) / 2
    : null;

  return (
    <div className="flex min-h-full flex-col">
      <PaperTradingBanner />

      <header className="border-b border-white/[0.09] px-6 py-6 sm:px-10">
        <div className="mx-auto max-w-6xl">
          <Link
            href="/"
            className="flex items-center gap-1 text-[12px] text-(--ink-muted) hover:text-(--ink-secondary)"
          >
            <ArrowLeft size={13} strokeWidth={2.25} /> Market Radar
          </Link>
          <div className="mt-2.5 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <h1 className="text-[28px] font-black tracking-tight">{data.ticker}</h1>
              <span className="tabular text-xl text-(--ink-secondary)">${data.price.toFixed(2)}</span>
            </div>
            <StatusBadge status={data.status} />
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 space-y-7 px-6 py-9 sm:px-10">
        {/* Belief comparison + forecast distribution */}
        <section className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="glass rounded-2xl p-5">
            <SectionTitle icon={Gauge}>AI Belief vs. Market Belief</SectionTitle>
            <div className="mt-4">
              <BeliefComparisonChart
                aiProbability={aiUpside ?? 0.5}
                marketProbability={data.market_implied_probability ?? 0.5}
              />
            </div>
          </div>
          <div className="glass rounded-2xl p-5">
            <SectionTitle icon={Sparkles}>AI Forecast Distribution</SectionTitle>
            <p className="mt-1.5 text-[12px] text-(--ink-muted)">
              {data.probability_forecast?.horizon ?? "—"} horizon · expected move{" "}
              {data.probability_forecast
                ? `${(data.probability_forecast.expected_move * 100).toFixed(1)}%`
                : "—"}
            </p>
            <div className="mt-1">
              <ProbabilityDistributionChart
                probabilities={data.probability_forecast?.probabilities ?? {}}
              />
            </div>
          </div>
        </section>

        <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatTile
            label="Divergence"
            value={
              data.divergence_score != null
                ? `${data.divergence_score >= 0 ? "+" : ""}${(data.divergence_score * 100).toFixed(1)}%`
                : "—"
            }
            accent={
              data.divergence_score != null && data.divergence_score >= 0
                ? "var(--belief-ai)"
                : "var(--belief-market)"
            }
          />
          <StatTile label="Opportunity score" value={data.opportunity_score.toFixed(3)} />
          <StatTile
            label="Forecast confidence"
            value={
              data.probability_forecast
                ? `${Math.round(data.probability_forecast.confidence * 100)}%`
                : "—"
            }
          />
          <StatTile
            label="Legs / strategy"
            value={data.proposed_trade ? data.proposed_trade.legs.length : "—"}
            hint={data.proposed_trade?.strategy_name.replaceAll("_", " ")}
          />
        </section>

        {/* Agent council */}
        <section>
          <SectionTitle icon={Sparkles}>Agent Council</SectionTitle>
          <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            {data.news_assessment && (
              <AgentCard
                name="News"
                role="Evidence"
                accent="var(--agent-news)"
                icon={Newspaper}
                direction={data.news_assessment.expected_direction}
                confidence={data.news_assessment.confidence}
                headline={data.news_assessment.what_changed}
                bullets={data.news_assessment.citations.map((c) => c.headline)}
              />
            )}
            {data.fundamental_assessment && (
              <AgentCard
                name="Fundamental"
                role="Company & sector"
                accent="var(--agent-fundamental)"
                icon={Building2}
                direction={data.fundamental_assessment.directional_bias}
                confidence={data.fundamental_assessment.confidence}
                headline={data.fundamental_assessment.evidence[0] ?? "No evidence cited."}
                bullets={data.fundamental_assessment.risks}
              />
            )}
            {data.probability_forecast && (
              <AgentCard
                name="Probability"
                role="Ensemble forecast"
                accent="var(--agent-probability)"
                icon={Sparkles}
                confidence={data.probability_forecast.confidence}
                headline={`Expected move ${(data.probability_forecast.expected_move * 100).toFixed(1)}% over ${data.probability_forecast.horizon}`}
                bullets={data.probability_forecast.evidence}
              />
            )}
            {data.diligence_report && <DiligenceReportCard report={data.diligence_report} />}
          </div>
        </section>

        {/* Trade proposal */}
        {data.proposed_trade && (
          <section>
            <SectionTitle icon={ClipboardList}>Trade Proposal</SectionTitle>
            <div className="mt-4">
              <TradeProposalCard
                trade={data.proposed_trade}
                riskApproved={data.risk_approved}
                riskNotes={data.risk_notes}
              />
            </div>
          </section>
        )}

        {data.evaluation_notes && (
          <section className="glass rounded-2xl p-5">
            <SectionTitle icon={ClipboardList}>Evaluator</SectionTitle>
            <p className="mt-2.5 text-[13px] leading-relaxed text-(--ink-secondary)">
              {data.evaluation_notes}
            </p>
          </section>
        )}
      </main>
    </div>
  );
}

function SectionTitle({
  children,
  icon: Icon,
}: {
  children: React.ReactNode;
  icon: React.ComponentType<{ size?: number; strokeWidth?: number; color?: string }>;
}) {
  return (
    <h2 className="flex items-center gap-1.5 text-[11.5px] font-bold uppercase tracking-[0.12em] text-(--ink-muted)">
      <Icon size={13} strokeWidth={2.25} />
      {children}
    </h2>
  );
}
