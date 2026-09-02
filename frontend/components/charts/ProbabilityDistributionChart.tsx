"use client";

import { Bar, BarChart, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const OUTCOME_ORDER = ["-10%", "-5%", "flat", "+5%", "+10%"];

function colorFor(outcome: string): string {
  if (outcome === "flat") return "var(--belief-neutral)";
  return outcome.startsWith("-") ? "var(--belief-market)" : "var(--belief-ai)";
}

interface TooltipPayloadItem {
  payload: { outcome: string; probability: number };
}

function ChartTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: TooltipPayloadItem[];
}) {
  if (!active || !payload?.length) return null;
  const { outcome, probability } = payload[0].payload;
  return (
    <div className="glass-strong rounded-lg px-3 py-2 text-[11px]">
      <div className="font-semibold text-[color:var(--ink-primary)]">{outcome}</div>
      <div className="tabular text-[color:var(--ink-secondary)]">
        {(probability * 100).toFixed(1)}% probability
      </div>
    </div>
  );
}

export function ProbabilityDistributionChart({
  probabilities,
}: {
  probabilities: Record<string, number>;
}) {
  const data = OUTCOME_ORDER.filter((o) => o in probabilities).map((outcome) => ({
    outcome,
    probability: probabilities[outcome],
  }));

  if (data.length === 0) {
    return (
      <div className="flex h-40 items-center justify-center text-[12px] text-[color:var(--ink-muted)]">
        No forecast distribution available.
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={160}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }} barCategoryGap="26%">
        <XAxis
          dataKey="outcome"
          axisLine={{ stroke: "rgba(21,24,41,0.12)" }}
          tickLine={false}
          tick={{ fill: "var(--ink-muted)", fontSize: 11 }}
        />
        <YAxis
          tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
          axisLine={false}
          tickLine={false}
          tick={{ fill: "var(--ink-muted)", fontSize: 10 }}
          width={40}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(21,24,41,0.035)" }} />
        <Bar dataKey="probability" radius={[4, 4, 4, 4]} maxBarSize={40}>
          {data.map((entry) => (
            <Cell key={entry.outcome} fill={colorFor(entry.outcome)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
