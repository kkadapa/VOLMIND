"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EquityPoint } from "@/lib/api";

const fmtUsd = (v: number) => `${v < 0 ? "-" : ""}$${Math.abs(v).toFixed(2)}`;

interface TooltipPayloadItem {
  payload: EquityPoint & { index: number };
}

function ChartTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayloadItem[] }) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  const pnlColor = point.realized_pnl >= 0 ? "var(--status-good)" : "var(--status-critical)";
  return (
    <div className="glass-strong rounded-lg px-3 py-2 text-[11px]">
      <div className="font-semibold text-[color:var(--ink-primary)]">
        {point.closed_at ? new Date(point.closed_at).toLocaleString() : `Trade ${point.index + 1}`}
      </div>
      <div className="tabular mt-1" style={{ color: pnlColor }}>
        this trade: {fmtUsd(point.realized_pnl)}
      </div>
      <div className="tabular text-[color:var(--ink-secondary)]">
        cumulative: {fmtUsd(point.cumulative_pnl)}
      </div>
    </div>
  );
}

export function EquityCurveChart({ equityCurve }: { equityCurve: EquityPoint[] }) {
  if (equityCurve.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center text-[12px] text-[color:var(--ink-muted)]">
        No closed trades yet — the equity curve fills in as positions close.
      </div>
    );
  }

  const data = equityCurve.map((point, index) => ({ ...point, index }));
  const finalPnl = data[data.length - 1].cumulative_pnl;
  const lineColor = finalPnl >= 0 ? "var(--status-good)" : "var(--status-critical)";

  return (
    <ResponsiveContainer width="100%" height={240}>
      <AreaChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="equityFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={lineColor} stopOpacity={0.22} />
            <stop offset="100%" stopColor={lineColor} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="rgba(21,24,41,0.06)" vertical={false} />
        <XAxis
          dataKey="index"
          tickFormatter={(v: number) => `#${v + 1}`}
          axisLine={{ stroke: "rgba(21,24,41,0.12)" }}
          tickLine={false}
          tick={{ fill: "var(--ink-muted)", fontSize: 10 }}
        />
        <YAxis
          tickFormatter={(v: number) => fmtUsd(v)}
          axisLine={false}
          tickLine={false}
          tick={{ fill: "var(--ink-muted)", fontSize: 10 }}
          width={64}
        />
        <ReferenceLine y={0} stroke="rgba(21,24,41,0.2)" strokeDasharray="3 3" />
        <Tooltip content={<ChartTooltip />} cursor={{ stroke: "rgba(21,24,41,0.15)" }} />
        <Area
          type="monotone"
          dataKey="cumulative_pnl"
          stroke={lineColor}
          strokeWidth={2}
          fill="url(#equityFill)"
          dot={{ r: 3, fill: lineColor, strokeWidth: 0 }}
          activeDot={{ r: 5, fill: lineColor, strokeWidth: 0 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
