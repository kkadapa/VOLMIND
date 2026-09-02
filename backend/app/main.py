from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.alpaca import trading
from app.config import get_settings
from app.memory.agent_reputation import PIPELINE_AGENTS, AgentReputation
from app.memory.opportunity_cache import OpportunityCache
from app.memory.trade_memory import TradeMemory
from app.models.trade import TradeStatus
from app.scheduler import start_scheduler, stop_scheduler
from app.services.position_monitor import PositionMonitor
from app.services.scanner import Scanner
from app.services.serialization import serialize_state
from app.services.streaming import stream_scan

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="VOLMIND", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "paper_trading": settings.alpaca_paper_trade,
        "llm_provider": settings.llm_provider,
        "autonomous_mode": settings.autonomous_mode,
    }


@app.get("/account")
def account() -> dict:
    acct = trading.get_account()
    return {
        "account_number": acct.account_number,
        "status": str(acct.status),
        "buying_power": float(acct.buying_power),
        "cash": float(acct.cash),
        "portfolio_value": float(acct.portfolio_value),
        "paper": True,
    }


@app.get("/positions")
def positions() -> list[dict]:
    return [
        {
            "symbol": p.symbol,
            "qty": float(p.qty),
            "market_value": float(p.market_value),
            "unrealized_pl": float(p.unrealized_pl),
        }
        for p in trading.get_open_positions()
    ]


@app.post("/positions/monitor")
def monitor_positions() -> list[dict]:
    """Manually trigger one position-monitor cycle (the autonomous loop calls this
    on its own schedule; exposed here so the UI/CLI can trigger it on demand)."""
    closed = PositionMonitor().run_cycle()
    return [trade.model_dump(mode="json") for trade in closed]


@app.post("/scan")
def scan(symbols: list[str]) -> list[dict]:
    scanner = Scanner()
    cache = OpportunityCache()
    results = scanner.scan(symbols)
    serialized = []
    for state in results:
        payload = serialize_state(state)
        cache.save(payload["ticker"], payload)
        serialized.append(payload)
    return serialized


@app.get("/scan/stream")
def scan_stream(symbols: str) -> StreamingResponse:
    """Server-sent events: one event per pipeline stage as it actually completes.

    `symbols` is a comma-separated query param (e.g. `?symbols=AAPL,MSFT`) since
    EventSource only issues GET requests.
    """
    ticker_list = [s for s in symbols.split(",") if s.strip()]
    return StreamingResponse(
        stream_scan(ticker_list),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/opportunities")
def list_opportunities() -> list[dict]:
    return OpportunityCache().list_all()


@app.get("/opportunities/{ticker}")
def get_opportunity(ticker: str) -> dict:
    result = OpportunityCache().get(ticker)
    if result is None:
        raise HTTPException(status_code=404, detail=f"No scan on record for {ticker.upper()}")
    return result


@app.get("/trades")
def list_trades() -> list[dict]:
    trades = TradeMemory().load_all()
    return [trade.model_dump(mode="json") for trade in trades]


@app.get("/performance")
def performance() -> dict:
    trades = TradeMemory().load_all()
    closed = [t for t in trades if t.status == TradeStatus.CLOSED and t.realized_pnl is not None]
    open_trades = [t for t in trades if t.status == TradeStatus.OPEN]
    wins = [t for t in closed if t.realized_pnl > 0]

    equity_curve = []
    cumulative = 0.0
    for trade in sorted(closed, key=lambda t: t.closed_at or datetime.min.replace(tzinfo=timezone.utc)):
        cumulative += trade.realized_pnl
        equity_curve.append(
            {
                "trade_id": trade.id,
                "closed_at": trade.closed_at.isoformat() if trade.closed_at else None,
                "realized_pnl": trade.realized_pnl,
                "cumulative_pnl": round(cumulative, 2),
            }
        )

    return {
        "total_realized_pnl": round(cumulative, 2),
        "win_rate": round(len(wins) / len(closed), 4) if closed else None,
        "open_count": len(open_trades),
        "closed_count": len(closed),
        "equity_curve": equity_curve,
    }


@app.get("/agents/reputation")
def agents_reputation() -> list[dict]:
    reputation = AgentReputation()
    return [reputation.get(name).model_dump(mode="json") for name in PIPELINE_AGENTS]
