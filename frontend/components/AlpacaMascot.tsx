export function AlpacaMascot() {
  return (
    <div className="flex flex-none flex-col items-center gap-2">
      <style>{`
        @keyframes alpaca-bob {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }
        @keyframes alpaca-blink {
          0%, 92%, 100% { transform: scaleY(1); }
          96% { transform: scaleY(0.15); }
        }
        @keyframes alpaca-ear {
          0%, 100% { transform: rotate(0deg); }
          50% { transform: rotate(-6deg); }
        }
        .alpaca-bob { animation: alpaca-bob 3.2s ease-in-out infinite; transform-origin: 70px 138px; }
        .alpaca-eye { animation: alpaca-blink 4.6s ease-in-out infinite; transform-origin: center; }
        .alpaca-ear-l { animation: alpaca-ear 3.2s ease-in-out infinite; transform-origin: 60px 16px; }
        .alpaca-ear-r { animation: alpaca-ear 3.2s ease-in-out infinite reverse; transform-origin: 80px 16px; }
        @media (prefers-reduced-motion: reduce) {
          .alpaca-bob, .alpaca-eye, .alpaca-ear-l, .alpaca-ear-r { animation: none; }
        }
      `}</style>
      <svg
        viewBox="0 0 140 150"
        width="88"
        height="94"
        role="img"
        aria-label="A small illustrated alpaca, VOLMIND's mascot for the Alpaca trading platform"
      >
        <g className="alpaca-bob">
          {/* legs */}
          <rect x="50" y="118" width="11" height="20" rx="4" fill="var(--ink-faint)" opacity="0.55" />
          <rect x="79" y="118" width="11" height="20" rx="4" fill="var(--ink-faint)" opacity="0.55" />

          {/* body */}
          <ellipse cx="70" cy="97" rx="40" ry="31" fill="var(--belief-market)" opacity="0.9" />
          <ellipse cx="70" cy="97" rx="40" ry="31" fill="none" stroke="var(--bg-page)" strokeOpacity="0.25" strokeWidth="1.5" />

          {/* neck */}
          <path d="M56,88 C54,64 56,42 62,26 L78,26 C84,42 86,64 84,88 Z" fill="var(--belief-market)" opacity="0.9" />

          {/* id tag */}
          <circle cx="70" cy="60" r="4" fill="var(--belief-ai)" />

          {/* ears */}
          <ellipse className="alpaca-ear-l" cx="60" cy="15" rx="4.5" ry="9" fill="var(--belief-market)" transform="rotate(-18 60 15)" />
          <ellipse className="alpaca-ear-r" cx="80" cy="15" rx="4.5" ry="9" fill="var(--belief-market)" transform="rotate(18 80 15)" />

          {/* head */}
          <circle cx="70" cy="26" r="17" fill="var(--belief-market)" />
          <circle cx="70" cy="26" r="17" fill="none" stroke="var(--bg-page)" strokeOpacity="0.25" strokeWidth="1.5" />

          {/* face */}
          <ellipse className="alpaca-eye" cx="63" cy="27" rx="2" ry="2.4" fill="var(--bg-page)" />
          <ellipse className="alpaca-eye" cx="77" cy="27" rx="2" ry="2.4" fill="var(--bg-page)" />
          <path d="M67,35 Q70,38 73,35" stroke="var(--bg-page)" strokeWidth="1.6" strokeLinecap="round" fill="none" opacity="0.6" />
        </g>
      </svg>
      <span className="text-[10px] uppercase tracking-[0.14em] text-(--ink-faint)">for Alpaca 🦙</span>
    </div>
  );
}
