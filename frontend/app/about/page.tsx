import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PaperTradingBanner } from "@/components/ui/PaperTradingBanner";
import { TopNav } from "@/components/ui/TopNav";
import { PipelineDiagram } from "@/components/PipelineDiagram";
import { AlpacaMascot } from "@/components/AlpacaMascot";

type Tok = { t: string; c?: string };
const g = "--status-good";
const f = "--ink-faint";
const b = "--belief-ai";
const m = "--belief-market";

const BOOT_LOG: Tok[][] = [
  [{ t: "$ ", c: f }, { t: "scan DIS" }],
  [
    { t: "news_agent", c: g },
    { t: "        " },
    { t: "▸ ", c: f },
    { t: "done      confidence " },
    { t: "0.55", c: b },
  ],
  [
    { t: "fundamental_agent", c: g },
    { t: " " },
    { t: "▸ ", c: f },
    { t: "done      confidence " },
    { t: "0.55", c: b },
  ],
  [
    { t: "probability_agent", c: g },
    { t: " " },
    { t: "▸ ", c: f },
    { t: "done      P(up) " },
    { t: "0.58", c: b },
  ],
  [
    { t: "divergence_agent", c: g },
    { t: "  " },
    { t: "▸ ", c: f },
    { t: "computed  AI " },
    { t: "0.58", c: b },
    { t: " vs market " },
    { t: "0.50", c: m },
  ],
  [
    { t: "diligence_agent", c: g },
    { t: "   " },
    { t: "▸ ", c: f },
    { t: "cleared   concern score " },
    { t: "0.20", c: b },
  ],
  [
    { t: "risk_agent", c: g },
    { t: "        " },
    { t: "▸ ", c: f },
    { t: "approved  within limits" },
  ],
  [
    { t: "execution", c: g },
    { t: "         " },
    { t: "▸ ", c: f },
    { t: "submitted  paper order" },
  ],
];

const BENEFITS = [
  {
    mark: "FAIL CLOSED",
    title: "Paper, always",
    body: "Execution refuses to run unless ALPACA_PAPER_TRADE is the literal string \"true\", checked on every order — opening and closing. The Alpaca client is separately hardcoded to paper mode as defense in depth.",
  },
  {
    mark: "MATERIALITY, NOT THEATER",
    title: "A gate that can say yes",
    body: "The diligence reviewer weighs whether a concern is severe enough to erase the edge — not whether it can find one. Every real option carries some risk; finding one isn't sufficient grounds to kill a trade.",
  },
  {
    mark: "PORTFOLIO AWARE",
    title: "Risk beyond one trade",
    body: "Per-trade max loss, a cap on concurrent open positions, and a daily realized-loss circuit breaker — a bad run stops the agent from digging in further the same day.",
  },
  {
    mark: "CLOSES THE LOOP",
    title: "P&L, not just picks",
    body: "A Position Monitor marks every open trade to market and force-closes it on schedule. That's what turns a signal into a number, and what lets agent reputation be scored against real outcomes.",
  },
];

const ROADMAP = [
  {
    when: "shipped",
    tone: "good" as const,
    title: "Single-leg options, one name at a time",
    body: "The Options Architect currently prices the nearest-ATM contract as a single long option — the simplest strategy that could prove the pipeline end to end.",
  },
  {
    when: "next",
    tone: "warn" as const,
    title: "Defined-risk spreads",
    body: "Vertical and calendar spreads, chosen by comparing several constructions' risk/reward against the diligence-reviewed edge, instead of always reaching for an unhedged long option.",
  },
  {
    when: "next",
    tone: "warn" as const,
    title: "Portfolio-level Greeks",
    body: "Today's risk gate looks at one trade and a position count. The natural next step is aggregate delta/vega exposure and correlation across open positions.",
  },
  {
    when: "later",
    tone: "muted" as const,
    title: "A human-in-the-loop terminal mode",
    body: "Scans triggered by an analyst, recommendations surfaced for sign-off, execution requiring a click — the same reasoning trail, a different consumer.",
  },
  {
    when: "later",
    tone: "muted" as const,
    title: "A live-mode readiness gate",
    body: "Not a toggle. A staged path with its own audit trail, position-size ramps, and kill-switch — treated with the same suspicion this system already applies to its own trade ideas.",
  },
];

function Kicker({ num, label }: { num: string; label: string }) {
  return (
    <div className="mb-5 flex items-baseline gap-3">
      <span className="text-[13px] text-(--ink-faint)">{num}</span>
      <span className="text-[12px] font-semibold uppercase tracking-[0.16em] text-(--ink-muted)">{label}</span>
      <span className="h-px flex-1 bg-white/[0.09]" />
    </div>
  );
}

export default function AboutPage() {
  return (
    <div className="flex min-h-full flex-col">
      <PaperTradingBanner />

      <header className="border-b border-white/[0.09] px-6 py-6 sm:px-10">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">About</h1>
            <p className="mt-1.5 text-[13px] text-(--ink-muted)">
              What VOLMIND is, how it decides, and where it&rsquo;s headed.
            </p>
          </div>
          <TopNav />
        </div>
      </header>

      <main className="mx-auto w-full max-w-5xl flex-1 px-6 py-14 sm:px-10">
        {/* Hero */}
        <section className="pb-20 text-center">
          <span
            className="inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-[11px] font-semibold uppercase tracking-[0.14em]"
            style={{ borderColor: "var(--border-glass)", background: "var(--bg-panel)", color: "var(--belief-market)" }}
          >
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: "var(--belief-market)" }} />
            Alpaca AI Trading Agents Hackathon
          </span>

          <h2
            className="mx-auto mt-7 text-[56px] font-black leading-none tracking-tight sm:text-[80px]"
            style={{
              background: "linear-gradient(135deg, var(--ink-primary) 40%, var(--belief-ai) 100%)",
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            VOLMIND
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-[18px] font-medium text-(--ink-secondary)">
            Trade the divergence between AI belief and market belief.
          </p>
          <p className="mx-auto mt-3 max-w-lg text-[13.5px] leading-relaxed text-(--ink-faint)">
            An autonomous, multi-agent options-research and trading terminal built on Alpaca —
            and a decision-support instrument a real desk could run alongside its existing tools.
          </p>

          <div className="mx-auto mt-10 flex max-w-3xl flex-col items-center gap-6 sm:flex-row sm:items-end sm:justify-center">
            <div className="glass-strong w-full max-w-xl rounded-xl text-left" style={{ borderRadius: 8 }}>
              <div className="flex items-center gap-1.5 border-b border-white/[0.09] px-3.5 py-2">
                <span className="h-2 w-2 rounded-full bg-white/20" />
                <span className="h-2 w-2 rounded-full bg-white/20" />
                <span className="h-2 w-2 rounded-full bg-white/20" />
                <span className="ml-2 text-[10px] uppercase tracking-[0.1em] text-(--ink-faint)">
                  volmind — live pipeline
                </span>
              </div>
              <div className="tabular overflow-x-auto px-4 py-4 text-[11.5px] leading-[1.9] whitespace-pre">
                {BOOT_LOG.map((line, i) => (
                  <div key={i}>
                    {line.map((tok, j) => (
                      <span key={j} style={tok.c ? { color: `var(${tok.c})` } : undefined}>
                        {tok.t}
                      </span>
                    ))}
                  </div>
                ))}
              </div>
            </div>

            <AlpacaMascot />
          </div>
        </section>

        {/* 01 why */}
        <section className="border-t border-white/[0.09] py-16">
          <Kicker num="01" label="Why this exists" />
          <h3 className="text-[26px] font-bold leading-tight tracking-tight sm:text-[32px]">
            Most &ldquo;AI trading agents&rdquo; stop at an opinion.
          </h3>
          <p className="mt-4 max-w-[65ch] text-[15.5px] leading-relaxed text-(--ink-secondary)">
            The hackathon brief asks for an agent that <strong className="text-(--ink-primary)">identifies opportunities,
            makes decisions, manages positions, and performs</strong> — not one that just narrates a hunch. VOLMIND&rsquo;s bet
            is narrower and more falsifiable than &ldquo;the model thinks it&rsquo;ll go up&rdquo;: it forms an independent
            probability estimate, compares it to what the options market is already pricing in, and only treats a large,
            well-evidenced gap between the two as a signal worth acting on.
          </p>
          <p className="mt-4 max-w-[65ch] text-[14.5px] leading-relaxed text-(--ink-muted)">
            A single LLM call agreeing with itself isn&rsquo;t a strategy. So the gap has to survive scrutiny before it
            becomes a trade: an independent second review that can kill the idea, a risk gate with hard dollar and
            position-count limits, and — the part most weekend projects skip — a monitor that actually closes the
            position later and turns it into a realized number.
          </p>
        </section>

        {/* 02 how it works */}
        <section className="border-t border-white/[0.09] py-16">
          <Kicker num="02" label="How it works" />
          <h3 className="text-[26px] font-bold leading-tight tracking-tight sm:text-[32px]">
            Two gates stand between a hunch and a paper order.
          </h3>
          <p className="mt-4 max-w-[68ch] text-[15.5px] leading-relaxed text-(--ink-secondary)">
            Three agents each form an independent view from live Alpaca data. Their combined belief is compared
            against the market&rsquo;s own option-implied probability. What survives has to clear{" "}
            <strong className="text-(--ink-primary)">diligence</strong> — an adversarial second read — and then{" "}
            <strong className="text-(--ink-primary)">risk</strong> — hard dollar and position limits — before a single
            order reaches Alpaca.
          </p>

          <figure className="mt-10">
            <PipelineDiagram />
            <figcaption className="mt-3.5 max-w-[75ch] text-[12.5px] leading-relaxed text-(--ink-faint)">
              Diligence is the one true branch — a flagged thesis skips straight to Evaluator, never reaching Options
              Architect. Risk is checked one step later, inside Execution itself: it can still keep an order from ever
              reaching Alpaca. Position Monitor runs separately, on its own schedule, and its close-out feeds each
              agent&rsquo;s win rate back into Agent Reputation.
            </figcaption>
          </figure>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/"
              className="glass-hover glass flex items-center gap-1.5 rounded-xl px-4 py-2.5 text-[13px] font-semibold text-(--ink-secondary)"
            >
              Watch it run live on Market Radar <ArrowRight size={14} strokeWidth={2.25} />
            </Link>
          </div>
        </section>

        {/* 03 what makes it different */}
        <section className="border-t border-white/[0.09] py-16">
          <Kicker num="03" label="What makes it different" />
          <h3 className="text-[26px] font-bold leading-tight tracking-tight sm:text-[32px]">
            Built to be distrusted by its own operator.
          </h3>
          <p className="mt-4 max-w-[65ch] text-[14.5px] leading-relaxed text-(--ink-muted)">
            Every mechanism below exists because the obvious version of this project would have quietly skipped it.
          </p>

          <div className="mt-8 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-white/[0.09] bg-white/[0.09] sm:grid-cols-2 lg:grid-cols-4">
            {BENEFITS.map((b) => (
              <div key={b.title} className="bg-(--bg-page-2) p-6">
                <div className="text-[10.5px] font-semibold uppercase tracking-[0.1em] text-(--ink-faint)">{b.mark}</div>
                <h4 className="mt-2.5 text-[15px] font-bold text-(--ink-primary)">{b.title}</h4>
                <p className="mt-2 text-[13px] leading-relaxed text-(--ink-muted)">{b.body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* 04 repurpose */}
        <section className="border-t border-white/[0.09] py-16">
          <Kicker num="04" label="Beyond the hackathon" />
          <h3 className="text-[26px] font-bold leading-tight tracking-tight sm:text-[32px]">
            The same pipeline, read instead of obeyed.
          </h3>
          <p className="mt-4 max-w-[68ch] text-[15.5px] leading-relaxed text-(--ink-secondary)">
            Strip out the scheduler and the auto-execution step, and what&rsquo;s left is a research terminal: a
            per-ticker feed of AI conviction versus market pricing, a reviewed reasoning trail, and a risk gate —
            the same shape as the pre-trade workflow already built into a desk&rsquo;s existing terminal, just running
            on an open pipeline instead of a closed one.
          </p>
          <p className="mt-4 max-w-[68ch] text-[14.5px] leading-relaxed text-(--ink-muted)">
            Point the graph at a scan a person triggers instead of a cron schedule, and it becomes something an
            analyst consults before advising a client — not a bot trading a book unattended. The autonomous loop
            demonstrated for the hackathon is one deployment mode of this system, not the only one it&rsquo;s built for.
          </p>
        </section>

        {/* 05 roadmap */}
        <section className="border-t border-white/[0.09] py-16">
          <Kicker num="05" label="What's next" />
          <h3 className="text-[26px] font-bold leading-tight tracking-tight sm:text-[32px]">
            Where this goes from a hackathon build.
          </h3>

          <div className="mt-8 flex flex-col">
            {ROADMAP.map((r, i) => (
              <div
                key={r.title}
                className="grid grid-cols-[92px_1fr] gap-5 border-t border-white/[0.09] py-5 sm:grid-cols-[120px_1fr]"
                style={i === ROADMAP.length - 1 ? { borderBottom: "1px solid var(--border-glass)" } : undefined}
              >
                <div
                  className="pt-0.5 text-[11px] font-semibold uppercase tracking-[0.1em]"
                  style={{
                    color:
                      r.tone === "good"
                        ? "var(--status-good)"
                        : r.tone === "warn"
                          ? "var(--status-warning-ink)"
                          : "var(--ink-faint)",
                  }}
                >
                  {r.when}
                </div>
                <div>
                  <h4 className="text-[14.5px] font-bold text-(--ink-primary)">{r.title}</h4>
                  <p className="mt-1.5 max-w-[60ch] text-[13px] leading-relaxed text-(--ink-muted)">{r.body}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* footer */}
        <section className="border-t border-white/[0.09] pt-14 text-center">
          <div
            className="mx-auto inline-flex items-center gap-2 rounded-lg border px-4 py-2.5 text-[11px] font-semibold uppercase tracking-[0.1em]"
            style={{
              borderColor: "color-mix(in srgb, var(--status-warning) 30%, transparent)",
              background: "color-mix(in srgb, var(--status-warning) 8%, transparent)",
              color: "var(--status-warning)",
            }}
          >
            <span className="h-1.5 w-1.5 rounded-full" style={{ background: "var(--status-warning)" }} />
            Paper trading only · no live orders are ever sent
          </div>
          <div className="mx-auto mt-6 flex max-w-lg flex-wrap items-center justify-center gap-x-4 gap-y-1.5 text-[11px] text-(--ink-faint)">
            <span>LangGraph orchestration</span>
            <span>·</span>
            <span>Alpaca market data &amp; execution</span>
            <span>·</span>
            <span>33 backend tests</span>
          </div>
        </section>
      </main>
    </div>
  );
}
