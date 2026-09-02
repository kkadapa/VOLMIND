"use client";

import {
  Building2,
  CheckCircle2,
  CircleDashed,
  GitCompareArrows,
  LineChart,
  Loader2,
  Newspaper,
  ScanSearch,
  SearchCheck,
  Send,
  ShieldCheck,
  Sparkles,
  XCircle,
} from "lucide-react";

export const PIPELINE_STEPS = [
  { node: "news", label: "News", icon: Newspaper },
  { node: "fundamental", label: "Fundamental", icon: Building2 },
  { node: "probability", label: "Probability", icon: Sparkles },
  { node: "market_probability", label: "Market Prob.", icon: LineChart },
  { node: "divergence", label: "Divergence", icon: GitCompareArrows },
  { node: "diligence", label: "Diligence", icon: SearchCheck },
  { node: "options_architect", label: "Options Architect", icon: ScanSearch },
  { node: "risk", label: "Risk", icon: ShieldCheck },
  { node: "execution", label: "Execution", icon: Send },
] as const;

export type StepState = "pending" | "running" | "done" | "skipped";

export function ScanProgress({
  ticker,
  completedNodes,
  finished,
  errored,
}: {
  ticker: string;
  completedNodes: Set<string>;
  finished: boolean;
  errored: boolean;
}) {
  const firstPendingIndex = PIPELINE_STEPS.findIndex((s) => !completedNodes.has(s.node));

  function stateFor(index: number, node: string): StepState {
    if (completedNodes.has(node)) return "done";
    if (errored) return "skipped";
    if (finished) return "skipped"; // pipeline ended (e.g. diligence review flagged the thesis) before reaching this step
    if (index === firstPendingIndex) return "running";
    return "pending";
  }

  return (
    <div className="glass rounded-2xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[13px] font-bold tracking-tight">{ticker}</span>
          <span className="text-[11px] text-(--ink-muted)">live agent pipeline</span>
        </div>
        {errored && (
          <span className="flex items-center gap-1 text-[11px] font-semibold text-(--status-critical)">
            <XCircle size={13} strokeWidth={2.25} /> failed
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-2.5">
        {PIPELINE_STEPS.map((step, i) => {
          const state = stateFor(i, step.node);
          const Icon = step.icon;
          return (
            <div
              key={step.node}
              className="flex min-w-[128px] flex-1 items-center gap-2 rounded-xl border px-3 py-2.5 transition-colors"
              style={{
                borderColor:
                  state === "done"
                    ? "color-mix(in srgb, var(--status-good) 35%, transparent)"
                    : state === "running"
                      ? "color-mix(in srgb, var(--belief-ai) 40%, transparent)"
                      : "var(--border-glass)",
                backgroundColor:
                  state === "done"
                    ? "color-mix(in srgb, var(--status-good) 8%, transparent)"
                    : state === "running"
                      ? "color-mix(in srgb, var(--belief-ai) 8%, transparent)"
                      : "transparent",
              }}
            >
              {state === "done" && (
                <CheckCircle2 size={16} strokeWidth={2.25} color="var(--status-good)" />
              )}
              {state === "running" && (
                <Loader2 size={16} strokeWidth={2.25} className="animate-spin" color="var(--belief-ai)" />
              )}
              {state === "pending" && <CircleDashed size={16} strokeWidth={2} color="var(--ink-faint)" />}
              {state === "skipped" && <Icon size={16} strokeWidth={2} color="var(--ink-faint)" />}
              <span
                className="text-[11.5px] font-medium"
                style={{
                  color:
                    state === "done"
                      ? "var(--status-good)"
                      : state === "running"
                        ? "var(--belief-ai)"
                        : "var(--ink-faint)",
                }}
              >
                {step.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
