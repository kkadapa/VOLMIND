export function PipelineDiagram() {
  return (
    <>
      <style>{`
        .dg-box{fill:var(--bg-page-2);stroke:var(--border-glass-strong);stroke-width:1;}
        .dg-box-accent{fill:color-mix(in srgb, var(--belief-ai) 8%, transparent);stroke:var(--belief-ai);stroke-width:1.25;}
        .dg-gate{fill:var(--bg-page-2);stroke:var(--ink-secondary);stroke-width:1.25;}
        .dg-tag{fill:none;stroke:var(--ink-faint);stroke-width:1;stroke-dasharray:3 3;}
        .dg-label{font-family:var(--font-mono);font-size:11.5px;fill:var(--ink-primary);font-weight:600;letter-spacing:.02em;}
        .dg-sublabel{font-family:var(--font-mono);font-size:9.5px;fill:var(--ink-faint);letter-spacing:.02em;}
        .dg-tagtext{font-family:var(--font-mono);font-size:9.5px;fill:var(--ink-faint);letter-spacing:.08em;}
        .dg-arrow{fill:none;stroke:var(--ink-faint);stroke-width:1.25;}
        .dg-arrow-yes{fill:none;stroke:var(--belief-ai);stroke-width:1.5;}
        .dg-arrow-no{fill:none;stroke:var(--status-critical);stroke-width:1.25;stroke-dasharray:4 3;}
        .dg-arrow-feedback{fill:none;stroke:var(--agent-diligence);stroke-width:1.25;stroke-dasharray:2 4;}
        .dg-edgelabel{font-family:var(--font-mono);font-size:9.5px;letter-spacing:.03em;}
        .dg-edgelabel.no{fill:var(--status-critical);}
        .dg-edgelabel.yes{fill:var(--belief-ai);}
        .dg-edgelabel.feedback{fill:var(--agent-diligence);}
        .dg-loop{fill:none;stroke:var(--ink-faint);stroke-width:1.1;}
      `}</style>
      <svg
        viewBox="0 0 1360 620"
        role="img"
        style={{ width: "100%", height: "auto" }}
        aria-label="Pipeline diagram: News and Fundamental agents feed the Probability agent, which forms an AI belief; independently, the live option chain feeds a deterministic Market-Implied Probability. Both converge into Divergence. Divergence feeds Diligence, the one true branch: a flagged thesis jumps straight to Evaluator, a cleared one continues to Options Architect and Risk. Risk, checked inside Execution, can still veto the order to Evaluator; an approved one executes as a paper order, then is watched by Position Monitor on a schedule until it closes on take-profit, stop-loss, or expiry, feeding the outcome back into Agent Reputation."
      >
        <defs>
          <marker id="ad-arrow-faint" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" style={{ fill: "var(--ink-faint)" }} />
          </marker>
          <marker id="ad-arrow-cyan" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" style={{ fill: "var(--belief-ai)" }} />
          </marker>
          <marker id="ad-arrow-red" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" style={{ fill: "var(--status-critical)" }} />
          </marker>
          <marker id="ad-arrow-violet" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
            <path d="M0,0 L10,5 L0,10 z" style={{ fill: "var(--agent-diligence)" }} />
          </marker>
        </defs>

        <text x="20" y="12" className="dg-tagtext">SIGNAL FORMATION</text>
        <text x="670" y="107" className="dg-tagtext">REVIEW</text>
        <text x="1150" y="132" className="dg-tagtext">EXECUTION &amp; CLOSE-OUT</text>

        <rect x="20" y="20" width="170" height="42" rx="6" className="dg-box" />
        <text x="105" y="46" textAnchor="middle" className="dg-label">NEWS</text>

        <rect x="20" y="92" width="170" height="42" rx="6" className="dg-box" />
        <text x="105" y="118" textAnchor="middle" className="dg-label">FUNDAMENTAL</text>

        <rect x="250" y="56" width="170" height="42" rx="6" className="dg-box" />
        <text x="335" y="79" textAnchor="middle" className="dg-label">PROBABILITY</text>
        <text x="335" y="91" textAnchor="middle" className="dg-sublabel">forms AI belief</text>

        <path d="M190,41 L220,41 L220,68 L250,68" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />
        <path d="M190,113 L220,113 L220,86 L250,86" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />

        <rect x="250" y="172" width="170" height="32" rx="5" className="dg-tag" />
        <text x="335" y="192" textAnchor="middle" className="dg-tagtext">LIVE OPTION CHAIN · no LLM</text>

        <rect x="250" y="234" width="170" height="42" rx="6" className="dg-box" />
        <text x="335" y="257" textAnchor="middle" className="dg-label">MARKET PROB.</text>
        <text x="335" y="269" textAnchor="middle" className="dg-sublabel">delta-approximated</text>

        <path d="M335,204 L335,234" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />

        <rect x="500" y="145" width="160" height="46" rx="6" className="dg-box" />
        <text x="580" y="170" textAnchor="middle" className="dg-label">DIVERGENCE</text>
        <text x="580" y="182" textAnchor="middle" className="dg-sublabel">AI &minus; market</text>

        <path d="M420,77 L460,77 L460,158 L500,158" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />
        <path d="M420,255 L460,255 L460,178 L500,178" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />

        <path d="M660,168 L670,168" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />
        <polygon points="760,122 850,168 760,214 670,168" className="dg-gate" />
        <text x="760" y="164" textAnchor="middle" className="dg-label">DILIGENCE</text>
        <text x="760" y="177" textAnchor="middle" className="dg-sublabel">materiality review</text>

        <path d="M760,214 L760,400 L740,440" className="dg-arrow-no" markerEnd="url(#ad-arrow-red)" />
        <text x="770" y="320" className="dg-edgelabel no">flagged · no trade</text>

        <path d="M850,168 L910,168" className="dg-arrow-yes" markerEnd="url(#ad-arrow-cyan)" />
        <text x="858" y="152" className="dg-edgelabel yes">cleared</text>

        <polygon points="1000,122 1090,168 1000,214 910,168" className="dg-gate" />
        <text x="1000" y="164" textAnchor="middle" className="dg-label">RISK</text>
        <text x="1000" y="177" textAnchor="middle" className="dg-sublabel">position &amp; $ limits</text>

        <path d="M1000,214 L1000,400 L790,440" className="dg-arrow-no" markerEnd="url(#ad-arrow-red)" />
        <text x="1006" y="320" className="dg-edgelabel no">vetoed</text>

        <rect x="660" y="440" width="210" height="50" rx="6" className="dg-box" />
        <text x="765" y="463" textAnchor="middle" className="dg-label">EVALUATOR</text>
        <text x="765" y="477" textAnchor="middle" className="dg-sublabel">always runs last · logs why</text>

        <path d="M1090,168 L1150,168" className="dg-arrow-yes" markerEnd="url(#ad-arrow-cyan)" />
        <text x="1096" y="152" className="dg-edgelabel yes">approved</text>

        <rect x="1150" y="145" width="170" height="46" rx="6" className="dg-box-accent" />
        <text x="1235" y="170" textAnchor="middle" className="dg-label">EXECUTION</text>
        <text x="1235" y="182" textAnchor="middle" className="dg-sublabel">paper order · Alpaca</text>

        <path d="M1235,191 L1235,245" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />
        <path d="M1195,245 C1195,213 1275,213 1275,245" className="dg-loop" markerEnd="url(#ad-arrow-faint)" />
        <text x="1235" y="205" textAnchor="middle" className="dg-tagtext">on a schedule</text>

        <rect x="1150" y="245" width="170" height="46" rx="6" className="dg-box-accent" />
        <text x="1235" y="270" textAnchor="middle" className="dg-label">POSITION MONITOR</text>
        <text x="1235" y="282" textAnchor="middle" className="dg-sublabel">marks to market</text>

        <path d="M1235,291 L1235,345" className="dg-arrow" markerEnd="url(#ad-arrow-faint)" />

        <rect x="1150" y="345" width="170" height="38" rx="5" className="dg-tag" />
        <text x="1235" y="368" textAnchor="middle" className="dg-tagtext">take-profit / stop-loss / expiry</text>

        <path d="M1150,364 C880,430 520,478 250,465" className="dg-arrow-feedback" markerEnd="url(#ad-arrow-violet)" />
        <text x="640" y="440" textAnchor="middle" className="dg-edgelabel feedback">closed trade scores every agent on realized P&amp;L</text>

        <rect x="20" y="440" width="230" height="50" rx="6" className="dg-box" />
        <text x="135" y="463" textAnchor="middle" className="dg-label">AGENT REPUTATION</text>
        <text x="135" y="477" textAnchor="middle" className="dg-sublabel">win rate per agent</text>
      </svg>
    </>
  );
}
