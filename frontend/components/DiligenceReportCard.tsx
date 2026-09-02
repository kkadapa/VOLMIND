import { SearchCheck, SearchX } from "lucide-react";
import type { DiligenceReport } from "@/lib/api";

export function DiligenceReportCard({ report }: { report: DiligenceReport }) {
  const color = report.passed ? "var(--status-good)" : "var(--status-critical)";
  const Icon = report.passed ? SearchCheck : SearchX;

  return (
    <div className="glass rounded-2xl p-5" style={{ borderLeft: `3px solid ${color}` }}>
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-start gap-2.5">
          <div
            className="mt-0.5 flex h-8 w-8 flex-none items-center justify-center rounded-lg"
            style={{ backgroundColor: `color-mix(in srgb, ${color} 14%, transparent)` }}
          >
            <Icon size={16} strokeWidth={2} color={color} />
          </div>
          <div>
            <div className="text-[14px] font-bold tracking-tight">Diligence Agent</div>
            <div className="text-[10.5px] uppercase tracking-[0.12em] text-(--ink-muted)">
              Independent pre-trade review
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
          {report.passed ? "CLEARED" : "FLAGGED"}
        </span>
      </div>

      <p className="mt-3.5 text-[13px] leading-relaxed text-(--ink-secondary)">
        {report.recommended_action}
      </p>

      {report.concerns.length > 0 && (
        <ReasonList title="Concerns" items={report.concerns} color={color} />
      )}
      {report.risks.length > 0 && (
        <ReasonList title="Risks" items={report.risks} color="var(--status-warning-ink)" />
      )}
      {report.missing_information.length > 0 && (
        <ReasonList
          title="Missing information"
          items={report.missing_information}
          color="var(--ink-muted)"
        />
      )}

      <div className="mt-4 flex items-center justify-between border-t border-white/[0.08] pt-3 text-[11.5px]">
        <span className="text-(--ink-muted)">Concern score</span>
        <span className="tabular font-semibold" style={{ color }}>
          {Math.round(report.concern_score * 100)}%
        </span>
      </div>
    </div>
  );
}

function ReasonList({ title, items, color }: { title: string; items: string[]; color: string }) {
  return (
    <div className="mt-3">
      <div className="text-[10.5px] font-semibold uppercase tracking-wide text-(--ink-muted)">
        {title}
      </div>
      <ul className="mt-1.5 space-y-1">
        {items.map((item, i) => (
          <li key={i} className="flex gap-1.5 text-[12px] leading-snug text-(--ink-secondary)">
            <span className="mt-1.5 h-1 w-1 flex-none rounded-full" style={{ backgroundColor: color }} />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
