from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel


class TradingBlockedError(RuntimeError):
    """Raised whenever code attempts to trade without an explicit paper-trading guarantee."""


class Settings(BaseModel):
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    # Fail closed: paper trading is only enabled when this is the literal string "true".
    # Anything else (unset, "false", typo) disables execution entirely.
    alpaca_paper_trade: bool = False

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5"

    # Featherless: OpenAI-compatible gateway to open-source models (api.featherless.ai).
    featherless_api_key: str = ""
    featherless_model: str = "Qwen/Qwen2.5-7B-Instruct"
    featherless_base_url: str = "https://api.featherless.ai/v1"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # CORS: which frontend origins may call this API. Defaults to local dev only;
    # a deployed frontend origin must be added explicitly via ALLOWED_ORIGINS.
    allowed_origins: list[str] = ["http://localhost:3000"]

    @property
    def llm_provider(self) -> str:
        # First configured key wins. Any one of these alone is sufficient --
        # agents degrade to neutral output when none are set.
        if self.anthropic_api_key:
            return "anthropic"
        if self.featherless_api_key:
            return "featherless"
        if self.openai_api_key:
            return "openai"
        return "none"

    max_position_risk: float = 500.0
    max_daily_loss: float = 1500.0
    min_divergence: float = 0.10
    min_confidence: float = 0.55

    # Position management
    max_open_positions: int = 3
    take_profit_pct: float = 0.50
    stop_loss_pct: float = 0.50
    min_days_to_expiry_exit: int = 1

    # Autonomous operation
    watchlist: list[str] = ["AAPL", "MSFT", "NVDA", "SPY"]
    scan_interval_minutes: int = 30
    monitor_interval_minutes: int = 5
    autonomous_mode: bool = False

    def require_paper_trading(self) -> None:
        if not self.alpaca_paper_trade:
            raise TradingBlockedError(
                "ALPACA_PAPER_TRADE is not set to 'true'. Refusing to execute any trade. "
                "VOLMIND never trades live and will not silently switch modes."
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        alpaca_api_key=os.getenv("ALPACA_API_KEY", ""),
        alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY", ""),
        alpaca_paper_trade=os.getenv("ALPACA_PAPER_TRADE", "").strip().lower() == "true",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
        featherless_api_key=os.getenv("FEATHERLESS_API_KEY", ""),
        featherless_model=os.getenv("FEATHERLESS_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        featherless_base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        allowed_origins=[
            s.strip()
            for s in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
            if s.strip()
        ],
        max_position_risk=float(os.getenv("VOLMIND_MAX_POSITION_RISK", "500")),
        max_daily_loss=float(os.getenv("VOLMIND_MAX_DAILY_LOSS", "1500")),
        min_divergence=float(os.getenv("VOLMIND_MIN_DIVERGENCE", "0.10")),
        min_confidence=float(os.getenv("VOLMIND_MIN_CONFIDENCE", "0.55")),
        # Note: VOLMIND_MAX_OPEN_TRADES, not _POSITIONS -- matches the name already
        # used in deployed .env files.
        max_open_positions=int(os.getenv("VOLMIND_MAX_OPEN_TRADES", "3")),
        take_profit_pct=float(os.getenv("VOLMIND_TAKE_PROFIT_PCT", "0.50")),
        stop_loss_pct=float(os.getenv("VOLMIND_STOP_LOSS_PCT", "0.50")),
        min_days_to_expiry_exit=int(os.getenv("VOLMIND_MIN_DAYS_TO_EXPIRY_EXIT", "1")),
        watchlist=[
            s.strip().upper()
            for s in os.getenv("VOLMIND_WATCHLIST", "AAPL,MSFT,NVDA,SPY").split(",")
            if s.strip()
        ],
        scan_interval_minutes=int(os.getenv("VOLMIND_SCAN_INTERVAL_MINUTES", "30")),
        monitor_interval_minutes=int(os.getenv("VOLMIND_MONITOR_INTERVAL_MINUTES", "5")),
        autonomous_mode=os.getenv("VOLMIND_AUTONOMOUS_MODE", "").strip().lower() == "true",
    )
