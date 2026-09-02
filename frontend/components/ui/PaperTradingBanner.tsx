export function PaperTradingBanner() {
  return (
    <div
      className="flex items-center justify-center gap-2 border-b py-1.5 text-[11px] font-bold tracking-[0.16em]"
      style={{
        borderColor: "color-mix(in srgb, var(--status-warning) 30%, transparent)",
        backgroundColor: "color-mix(in srgb, var(--status-warning) 10%, transparent)",
        color: "var(--status-warning)",
      }}
    >
      <span
        className="h-1.5 w-1.5 animate-pulse rounded-full"
        style={{ backgroundColor: "var(--status-warning)" }}
        aria-hidden
      />
      PAPER TRADING ONLY · NO LIVE ORDERS ARE EVER SENT
    </div>
  );
}
