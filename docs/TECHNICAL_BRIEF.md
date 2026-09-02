# VOLMIND — Technical Brief

**Options Alpha Agents — one-page write-up: AI logic, risk gates, Alpaca infrastructure.**

Trade the divergence between AI belief and market belief: a LangGraph pipeline forms an
independent probability estimate, compares it against the option chain's own implied
probability, and routes only diligence- and risk-cleared theses to paper execution.

```
News → Fundamental → Probability → Market-Implied Probability → Divergence
     → Diligence [gate] ─cleared→ Options Architect → Risk [gate] → Execution → Evaluator
```

## 1. AI Logic — belief formation

- **Belief agents** (News, Fundamental, Probability) each call an LLM through
  `structured_completion` (`backend/app/llm.py`) and return a Pydantic-validated
  forecast, not free text. **Evidence-required clamping**: a forecast that cites no
  evidence has its confidence forced toward a neutral prior before it can influence
  anything downstream.
- **Provider-agnostic**: first configured key wins — `ANTHROPIC_API_KEY`
  (`claude-haiku-4-5`) → `FEATHERLESS_API_KEY` → `OPENAI_API_KEY`. Every call retries
  up to 3× and returns `None` rather than raising, so one failed LLM call degrades a
  single agent to "no opinion" instead of crashing the pipeline.
- **Market-implied probability** (`backend/app/quant/implied_probability.py`) is
  computed directly from the live Alpaca option chain, independent of the LLM — a
  near-the-money call's delta stands in for P(price above spot at expiry).
- **Divergence** = AI probability − market-implied probability. A thesis is only
  interesting once this gap and the forecast's confidence both clear configured
  thresholds (see Risk Gates below).
- **Reputation loop** (`backend/app/memory/agent_reputation.py`): every closed trade
  scores the five belief/gating agents (news, fundamental, probability, diligence,
  risk) against the real outcome — correct-count / trade-count plus a Brier score,
  updated on every close.

## 2. Risk Gates — fail-closed by default, checked on every trade

1. **Diligence Agent** — an independent second LLM pass (adversarial review, not a
   rubber stamp) plus two deterministic floor checks the model can't argue past:
   `|divergence| ≥ 0.10` and `confidence ≥ 0.55` (both configurable). Failing either
   halts the graph before a strategy is even priced — no proposal, no risk check, no
   order.
2. **Risk Agent** — three independent, portfolio-level vetoes evaluated fresh each
   time: open positions `≥ VOLMIND_MAX_OPEN_TRADES` (default 3); today's realized
   loss past `VOLMIND_MAX_DAILY_LOSS` (default $1,500); per-trade
   `max_loss × qty × 100` past `VOLMIND_MAX_POSITION_RISK` (default $500).
3. **Paper-trade guard** — `Settings.require_paper_trading()` raises unless
   `ALPACA_PAPER_TRADE` is the exact string `"true"`, called immediately before
   *every* order, opening or closing. `TradingClient` is separately hardcoded
   `paper=True` at construction, so a bypassed guard still can't reach a live
   endpoint.
4. **Position Monitor** — every open position is marked to market each cycle; the
   first rule to trip closes it: days-to-expiry cutoff (default 1 day, avoids
   pin/assignment risk) → take-profit (default +50%) → stop-loss (default −50%).
5. **Market-hours gate** — autonomous mode is opt-in
   (`VOLMIND_AUTONOMOUS_MODE=false` by default); every scheduled cycle checks
   Alpaca's own clock first and skips entirely while the market is closed.

Every agent decision is logged with a trace ID, input, output, confidence, and reason
(`backend/app/observability.py`) — a blocked trade always has an inspectable paper
trail, never a silent no.

## 3. Alpaca Infrastructure — `alpaca-py`, four scoped clients

- **Trading** (`TradingClient`) — account, positions, order submission and closes.
  Single-leg theses ship as a `LimitOrderRequest`; the multi-leg path
  (`OrderClass.MLEG` + `OptionLegRequest`) is already wired for when the strategy
  pricer grows past single calls/puts.
- **Options data** (`OptionHistoricalDataClient`) — `OptionChainRequest` pulls the
  full live chain (bid, ask, IV, Greeks) per OCC contract for Scout and Architect;
  `OptionLatestQuoteRequest` re-quotes each open position every Position Monitor
  cycle.
- **Market data / news** — live underlying quotes feed opportunity discovery; Alpaca
  news (with citations) feeds the News Agent's LLM assessment directly — no
  synthetic or cached headlines.
- **Clock** (`get_clock()`) — Alpaca's own market clock gates every autonomous scan
  and monitor cycle; the agent never trades against a closed tape.
- **Autonomous runtime** — in-process `APScheduler` jobs (scan every 30 min, monitor
  every 5 min, both configurable) inside the FastAPI app, or the same cycle
  functions as a standalone long-lived process (`scripts/run_autonomous.py`) — built
  to run unattended for the length of a competition.
- **Persistence** — trades, predictions, and agent reputation write to local JSON
  stores: an auditable, restartable ledger with no external dependency to stand up.

---

**10** pipeline nodes · **5** agents scored on P&L · **3** independent risk vetoes ·
**33** tests passing (`pytest backend/tests`)

Paper trading only — `ALPACA_PAPER_TRADE` is fail-closed by default.
