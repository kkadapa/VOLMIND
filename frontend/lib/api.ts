export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Direction = "bullish" | "bearish" | "neutral";

export interface Citation {
  headline: string;
  source: string | null;
  url: string | null;
  published_at: string | null;
}

export interface NewsAssessment {
  agent_name: string;
  underlying_symbol: string;
  what_changed: string;
  why_it_matters: string;
  is_new_information: boolean;
  expected_direction: Direction;
  expected_magnitude: number;
  confidence: number;
  citations: Citation[];
}

export interface FundamentalAssessment {
  agent_name: string;
  underlying_symbol: string;
  directional_bias: Direction;
  probability_estimate: number;
  confidence: number;
  evidence: string[];
  risks: string[];
}

export interface ProbabilityForecast {
  ticker: string;
  event: string;
  horizon: string;
  probabilities: Record<string, number>;
  expected_move: number;
  confidence: number;
  evidence: string[];
  model_version: string;
}

export interface DiligenceReport {
  passed: boolean;
  concern_score: number;
  concerns: string[];
  risks: string[];
  missing_information: string[];
  recommended_action: string;
  confidence: number;
}

export interface OptionLeg {
  symbol: string;
  option_type: "call" | "put";
  strike: number;
  expiry: string;
  bid: number;
  ask: number;
  implied_volatility: number | null;
  delta: number | null;
  gamma: number | null;
  theta: number | null;
  vega: number | null;
}

export interface ProposedTrade {
  id: string;
  strategy_name: string;
  legs: OptionLeg[];
  quantity: number;
  entry_cost: number;
  max_loss: number;
  max_profit: number | null;
  status: string;
}

export type TradeStatus = "proposed" | "open" | "closed" | "rejected";

export interface Trade {
  id: string;
  opportunity_id: string;
  underlying_symbol: string;
  strategy_name: string;
  legs: OptionLeg[];
  quantity: number;
  entry_cost: number;
  max_loss: number;
  max_profit: number | null;
  status: TradeStatus;
  opened_at: string | null;
  closed_at: string | null;
  realized_pnl: number | null;
}

export interface EquityPoint {
  trade_id: string;
  closed_at: string | null;
  realized_pnl: number;
  cumulative_pnl: number;
}

export interface PerformanceSummary {
  total_realized_pnl: number;
  win_rate: number | null;
  open_count: number;
  closed_count: number;
  equity_curve: EquityPoint[];
}

export type OpportunityStatus =
  | "screening"
  | "no_trade_diligence"
  | "no_trade_risk"
  | "cleared";

export interface ScannedOpportunity {
  trace_id: string | null;
  ticker: string;
  price: number;
  discovered_at: string;
  news_assessment: NewsAssessment | null;
  fundamental_assessment: FundamentalAssessment | null;
  probability_forecast: ProbabilityForecast | null;
  market_implied_probability: number | null;
  divergence_score: number | null;
  opportunity_score: number;
  diligence_report: DiligenceReport | null;
  proposed_trade: ProposedTrade | null;
  executed_trade: Trade | null;
  risk_approved: boolean | null;
  risk_notes: string | null;
  evaluation_notes: string | null;
  status: OpportunityStatus;
}

export interface HealthResponse {
  status: string;
  paper_trading: boolean;
  llm_provider: string;
  autonomous_mode: boolean;
}

export interface PositionSnapshot {
  symbol: string;
  qty: number;
  market_value: number;
  unrealized_pl: number;
}

export interface AccountSnapshot {
  account_number: string;
  status: string;
  buying_power: number;
  cash: number;
  portfolio_value: number;
  paper: boolean;
}

export interface AgentReputationEntry {
  agent_name: string;
  trade_count: number;
  correct_count: number;
  brier_score: number;
  reputation_weight: number;
  updated_at: string;
}

export type ScanEvent =
  | { type: "symbol_start"; ticker: string }
  | { type: "agent_done"; ticker: string; node: string; label: string }
  | { type: "symbol_error"; ticker: string; message: string }
  | { type: "opportunity_complete"; ticker: string; data: ScannedOpportunity }
  | { type: "scan_complete" };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${init?.method ?? "GET"} ${path} -> ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  account: () => request<AccountSnapshot>("/account"),
  positions: () => request<PositionSnapshot[]>("/positions"),
  opportunities: () => request<ScannedOpportunity[]>("/opportunities"),
  opportunity: (ticker: string) =>
    request<ScannedOpportunity>(`/opportunities/${ticker}`),
  scan: (symbols: string[]) =>
    request<ScannedOpportunity[]>("/scan", {
      method: "POST",
      body: JSON.stringify(symbols),
    }),
  /** Live pipeline progress via server-sent events -- one event per agent as it
   * actually completes. Returns the EventSource so the caller can close it. */
  streamScan: (symbols: string[], onEvent: (event: ScanEvent) => void): EventSource => {
    const url = `${API_BASE}/scan/stream?symbols=${encodeURIComponent(symbols.join(","))}`;
    const source = new EventSource(url);
    source.onmessage = (message) => {
      try {
        onEvent(JSON.parse(message.data) as ScanEvent);
      } catch {
        // Ignore a malformed frame rather than tearing down the whole stream.
      }
    };
    return source;
  },
  reputation: () => request<AgentReputationEntry[]>("/agents/reputation"),
  trades: () => request<Trade[]>("/trades"),
  performance: () => request<PerformanceSummary>("/performance"),
  monitorPositions: () =>
    request<Trade[]>("/positions/monitor", { method: "POST" }),
};
